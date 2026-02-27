# 4. Uticaj posete StackOverflow-a na platu i staz

## Opis upita
Pronađi programere koji posećuju StackOverflow sajt svakodnevno (`SOVisitFreq = 'Daily or almost daily'`) u odnosu na one koji posećuju SO retko (`'A few times per month or weekly'`). Izračunaj prosečnu platu i radni staž svakog tipa posetioca i grupiši rezultate po zemlji.

## Query (v2)

```javascript
db.getCollection('so_migration_stats').aggregate([
	{
    
		// Grupisem po drzavi
		$group: {
			_id: "$country",
			uporednaStatistika: {
				$push: {
					tipPosetioca: "$visitFreq",
					plata: { $round: ["$avgSalary", 2] },
					staz: { $round: ["$avgExp", 1] },
					brojLjudi: "$count"
				}
			}
		}
	},
	{
		$project: {
			_id: 0,
			drzava: "$_id",
			uporednaStatistika: "$uporednaStatistika"
		}
	},
	{ $sort: { "drzava": 1 } }
])
```
