# 2. Dubinska analiza veštačke inteligencije (AI)

## Opis upita
Grupišite developere po tome da li trenutno koriste alate za veštačku inteligenciju (AISelect = 'Yes') i izračunajte prosečnu platu za svaku od te dve grupe (Yes/No) u Srbiji i izračunati procenat onih koji uče preko knjiga i onih koji su stekli znanje od prijatelja (LearnCode). Sortirajte rezultate od najviše do najniže prosečne plate.

## Query (v2)

```javascript
db.getCollection('developers2').aggregate([
  {
    
    $match: {
      "ConvertedCompYearly": { $gt: 0 },
     "Country": "Serbia",
      "AISelect": { $exists: true } 
    }
  },
  {
    
    $group: {
      _id: {
        drzava: "$Country",
        koristiAI: "$AISelect"
      },
      prosecnaPlata: { $avg: "$ConvertedCompYearly" },
      ukupnoLjudiUGrupi: { $sum: 1 },
      
    
      uciKnjige: {
        $sum: {
          $cond: [{ $in: ["Books / Physical media", { $ifNull: ["$LearnCode", []] }] }, 1, 0]
        }
      },
      uciPrijatelji: {
        $sum: {
          $cond: [{ $in: ["Friend or family member", { $ifNull: ["$LearnCode", []] }] }, 1, 0]
        }
      }
    }
  },
  {
    
    
    $project: {
      _id: 0,
      drzava: "$_id.drzava",
      koristiAI: "$_id.koristiAI",
      prosecnaPlata: { $round: ["$prosecnaPlata", 2] },
      procenti: {
        knjige: { 
          $round: [{ $multiply: [{ $divide: ["$uciKnjige", "$ukupnoLjudiUGrupi"] }, 100] }, 2] 
        },
        prijatelji: { 
          $round: [{ $multiply: [{ $divide: ["$uciPrijatelji", "$ukupnoLjudiUGrupi"] }, 100] }, 2] 
        }
      },
      brojIspitanika: "$ukupnoLjudiUGrupi"
    }
  },
  { $sort: { prosecnaPlata: -1 } }
])
```
