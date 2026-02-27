# 5. Dubinska analiza odnosa između industrije i zadovoljstva

## Opis upita
Za svaku industriju izračunati prosečnu platu i prosečno zadovoljstvo poslom. Pored toga, prikazati najkorisćeniju bazu podataka i procenat zaposlenih koji su veoma zadovoljni poslom (`JobSat` 9 ili 10).

## Index
```javascript
db.technologies.createIndex({ ResponseId: 1 })
```

## Query

```javascript
db.getCollection('developers').aggregate([
  {

    $match: {
      "Industry": { $type: "string", $nin: [null, "NaN", "Other"] },
      "JobSat": { $type: "number", $gte: 1, $lte: 10 },
      "ConvertedCompYearly": { $type: "number", $gt: 0 }
    }
  },
  {
      
    //  LOOKUP
    $lookup: {
      from: "technologies",
      localField: "ResponseId",
      foreignField: "ResponseId",
      as: "techData"
    }
  },
  {
   
    $unwind: "$techData"
  },
  {
    //  Razbijemm niz baza
    $unwind: "$techData.DatabaseHaveWorkedWith"
  },
  {
    // Brojim baze unutar industrije
    
    $group: {
      _id: {
        industrija: "$Industry",
        baza: "$techData.DatabaseHaveWorkedWith"
      },
      prosecnaPlata: { $avg: "$ConvertedCompYearly" },
      prosecnoZadovoljstvo: { $avg: "$JobSat" },
      brojPojavljivanjaBaze: { $sum: 1 },
      brojEkstremnoSrecnih: {
        $sum: { $cond: [{ $gte: ["$JobSat", 9] }, 1, 0] }
      }
    }
  },
  {
    // Najpopularnija baza po industriji na vrh
    $sort: { "_id.industrija": 1, "brojPojavljivanjaBaze": -1 }
  },
  {
    // Uzimam 1. bazu za svaku industriju -- samo PO INDUSTRIJI GRUOP
    $group: {
      _id: "$_id.industrija",
      najcescaBaza: { $first: "$_id.baza" },
      plata: { $avg: "$prosecnaPlata" },
      zadovoljstvo: { $avg: "$prosecnoZadovoljstvo" },
      ukupnoSrecnih: { $sum: "$brojEkstremnoSrecnih" },
      ukupnoIspitanika: { $sum: "$brojPojavljivanjaBaze" }
    }
  },
  {
    
    $project: {
      _id: 0,
      industrija: "$_id",
      najcescaBaza: 1,
      prosecnaPlataUSD: { 
        $concat: [ { $literal: "$$" }, { $toString: { $round: ["$plata", 2] } } ] 
      },
      skalaZadovoljstva: { $round: ["$zadovoljstvo", 2] },
      procenatSrece: {
        $concat: [
          { $toString: { $round: [{ $multiply: [{ $divide: ["$ukupnoSrecnih", "$ukupnoIspitanika"] }, 100] }, 2] } },
          "%"
        ]
      }
    }
  },
  {
    $sort: { "skalaZadovoljstva": -1 }
  }
])
```