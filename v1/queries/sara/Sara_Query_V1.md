# 1. Korelacija popularnosti programskog jezika i plate

## Opis upita
Koja je prosečna godišnja plata (ConvertedCompYearly) za developere koji koriste i Python i JavaScript u poređenju sa onima koji koriste samo Python ili samo JavaScript?

## Index
```javascript
db.technologies.createIndex({ ResponseId: 1 })
```

## Query

```javascript
db.getCollection('developers').aggregate([
  {
    
    $match: {
      "ConvertedCompYearly": { $exists: true, $ne: NaN }
    }
  },
  
  {
      
      
    $lookup: {
      from: "technologies",
      localField: "ResponseId",
      foreignField: "ResponseId",
      as: "tech_info"
    }
  },
  
  
  {
    $unwind: "$tech_info"
  },
  {
    $project: {
      salary: "$ConvertedCompYearly",
      group: {
        $let: {
          vars: {
            
            hasPython: { $in: ["Python", "$tech_info.LanguageHaveWorkedWith"] },
            hasJS: { $in: ["JavaScript", "$tech_info.LanguageHaveWorkedWith"] }
          },
          in: {
            $cond: [
              { $and: ["$$hasPython", "$$hasJS"] }, "Both (Python & JS)",
              { $cond: ["$$hasPython", "Only Python", 
                { $cond: ["$$hasJS", "Only JS", "Other"] }
              ]}
            ]
          }
          
        }
      }
    }
  },
  {
    $match: { group: { $ne: "Other" } }
  },
  {
    $group: {
      _id: "$group",
      averageSalary: { $avg: "$salary" },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { averageSalary: -1 }
  }
])
```


