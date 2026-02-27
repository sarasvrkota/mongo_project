# 3. Iskustvo po veličini kompanije i top jezici

## Opis upita
Izračunajte prosečno radno iskustvo (YearsCodePro) za developere u kompanijama sa različitim brojem zaposlenih (OrgSize). Za svaku veličinu kompanije prikažite i tri najpopularnija programska jezika među ispitaniсima.

## Query (v2)

```javascript
db.getCollection('org_size_computed').aggregate([
	{
		// 1. Sortiramo  brojuj korisnika
		$sort: { "count": -1 }
	},
	{
		// onda group po velicini firme al samo jedan
		$group: {
			_id: "$orgSize",
			// Uzimamo prosek proseka
			stazProsek: { $avg: "$avgExp" },
			//  $first uzima naj starosnu grupu 
				 najcescaStarosnaGrupa: { $first: "$age" },
			popularniJezici: {
				$push: {
					jezik: "$jezik",
					korisnika: "$count"
				}
			}
		}
	},
	{

		$project: {
			_id: 0,
			najcescaStarosnaGrupa: 1,
			velicinaKompanije: "$_id",
			stazProsek: { $round: ["$stazProsek", 1] },
			top3Jezika: { $slice: ["$popularniJezici", 3] }
		}
	},
	{
   
		$sort: { "stazProsek": 1 }
	}
])
```
