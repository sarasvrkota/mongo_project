# 5. Dubinska analiza odnosa između industrije i zadovoljstva

## Opis upita
Za svaku industriju izračunati prosečnu platu i prosečno zadovoljstvo poslom. Pored toga, prikazati najkorisćeniju bazu podataka i procenat zaposlenih koji su veoma zadovoljni poslom (`JobSat` 9 ili 10).

## Query (v2)

```javascript
db.getCollection('developers2').aggregate([
	{
		$match: {
			"Industry": { $type: "string", $nin: [null, "NaN", "Other"] },
			"JobSat": { $type: "number", $gte: 1, $lte: 10 },
			"ConvertedCompYearly": { $type: "number", $gt: 0 },
			"DatabaseHaveWorkedWith": { $exists: true, $not: { $size: 0 } }
		}
	},
	{ $unwind: "$DatabaseHaveWorkedWith" },
	{
		$group: {
			_id: { ind: "$Industry", baza: "$DatabaseHaveWorkedWith" },
			plataInd: { $avg: "$ConvertedCompYearly" },
			satInd: { $avg: "$JobSat" },
			countBaza: { $sum: 1 },
			srecni: { $sum: { $cond: [{ $gte: ["$JobSat", 9] }, 1, 0] } }
		}
	},
	{ $sort: { "countBaza": -1 } },
	{
		$group: {
			_id: "$_id.ind",
			najcescaBaza: { $first: "$_id.baza" },
			avgPlata: { $avg: "$plataInd" },
			avgSat: { $avg: "$satInd" },
			ukupnoSrecnih: { $sum: "$srecni" },
			ukupnoUzoraka: { $sum: "$countBaza" }
		}
	},
	{
		$project: {
			_id: 0,
			industrija: "$_id",
			najcescaBaza: 1,
     
			prosecnaPlataUSD: { 
				$concat: [ 
					{ $literal: "$$" }, 
					{ $toString: { $round: ["$avgPlata", 2] } } 
				] 
			},
     
			skalaZadovoljstva: { $round: ["$avgSat", 2] },
    
			procenatSrece: {
				$concat: [
					{ $toString: { $round: [{ $multiply: [{ $divide: ["$ukupnoSrecnih", "$ukupnoUzoraka"] }, 100] }, 2] } },
					"%"
				]
			}
		}
	},
	{ $sort: { "skalaZadovoljstva": -1 } }
])
```
