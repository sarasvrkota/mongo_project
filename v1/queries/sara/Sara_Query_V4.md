# 4. Uticaj posete StackOverflow-a na platu i staz

## Opis upita
Pronađi programere koji posećuju StackOverflow sajt svakodnevno (`SOVisitFreq = 'Daily or almost daily'`) u odnosu na one koji posećuju SO retko (`'A few times per month or weekly'`). Izračunaj prosečnu platu i radni staž svakog tipa posetioca i grupiši rezultate po zemlji.

## Query

```javascript
db.getCollection('developers').aggregate([
  {
    //    1.FILTER: Uzimamo samo dve ciljne gr i one sa validnom platom i iskustvom

    $match: {
      "SOVisitFreq": { 
        $in: ["Daily or almost daily", "A few times per month or weekly"] 
      },
      "ConvertedCompYearly": {$ne: NaN  },
      "YearsCodePro": { $ne: NaN  }
    }
  },
  {
    // Po zemljii i po ucestalosti posete
    $group: {
      _id: {
        drzava: "$Country",
        ucestalost: "$SOVisitFreq"
      },
      prosecnaPlata: { $avg: "$ConvertedCompYearly" },
      prosecanStaz: { $avg: "$YearsCodePro" },
      brojIspitanika: { $sum: 1 }
    }
  },
  {
    
    $sort: { "_id.drzava": 1, "_id.ucestalost": 1 }
  },
  {
    // DRUGO GRUPISANJE uzimam obe grupe u jedan dokument po drzavi grupism 
    $group: {
      _id: "$_id.drzava",
      podaci: {
        $push: {
          tipPosetioca: "$_id.ucestalost",
          plata: { $round: ["$prosecnaPlata", 2] },
          staz: { $round: ["$prosecanStaz", 1] },
          brojLjudi: "$brojIspitanika"
        }
      }
    }
  },
  {

    $project: {
      _id: 0,
      drzava: "$_id",
      uporednaStatistika: "$podaci"
    }
  },
  {
    //  SORT Po abecedi drzava
    $sort: { "drzava": 1 }
  }
])
```