# 2. Dubinska analiza veštačke inteligencije (AI)

## Opis upita
Grupišite developere po tome da li trenutno koriste alate za veštačku inteligenciju (AISelect = 'Yes') i izračunajte prosečnu platu za svaku od te dve grupe (Yes/No) u Srbiji i izračunati procenat onih koji uče preko knjiga i onih koji su stekli znanje od prijatelja (LearnCode). Sortirajte rezultate od najviše do najniže prosečne plate.

## Query

```javascript
db.getCollection('developers').aggregate([
  {
    
    $match: {
        "Country": "Serbia",
      "ConvertedCompYearly": { $type: "number", $gt: 0 },
      
    }
  },
  
  
  {
    // JOIN da dobijem AISelect i LearnCode 
    $lookup: {
      from: "technologies",
      localField: "ResponseId",
      foreignField: "ResponseId",
      as: "tech"
    }
  },
  
  
  
  { $unwind: "$tech"   },
  
  {
    // grupise Po zemlji i AI statusu
    $group: {
      _id: {
        drzava: "$Country",
        koristiAI: "$tech.AISelect"
      },
      
      
      prosecnaPlata: { $avg: "$ConvertedCompYearly" },
      ukupnoLjudiUGrupi: { $sum: 1 },
      
      // Brojimo koliko ljudi ucii preko knjiga
      uciKnjige: {
        $sum: {
          $cond: [{ $in: ["Books / Physical media", { $ifNull: ["$LearnCode", []] }] }, 1, 0]
        }
      },
      // i preko prijatelja/porodice
      uciPrijatelji: {
        $sum: {
          $cond: [{ $in: ["Friend or family member", { $ifNull: ["$LearnCode", []] }] }, 1, 0]
        }
      }
    }
  },
  
  
  {
    // PROJEKCIJA --- procenati 
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
  
  
  
  {
    // 5. SORTIRANJE: Od najveće plate ka najmanjoj
    $sort: { prosecnaPlata: -1 }
  }
])
```