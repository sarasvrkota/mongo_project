# 1. Korelacija popularnosti programskog jezika i plate

## Opis upita
Koja je prosečna godišnja plata (ConvertedCompYearly) za developere koji koriste i Python i JavaScript u poređenju sa onima koji koriste samo Python ili samo JavaScript?

## Query (v2 - developers2 collection)

```javascript
db.getCollection('developers2').aggregate([
  {
    // Filtriramo samo one koji imaju platu i koji koriste Python ili JS
    $match: {
      "ConvertedCompYearly": { $gt: 0 },
      "LanguageHaveWorkedWith": { $in: ["Python", "JavaScript"] }
    }
  },
  {
    // LogiKa ista
    $project: {
      salary: "$ConvertedCompYearly",
      group: {
        $let: {
          vars: {
            hasPython: { $in: ["Python", "$LanguageHaveWorkedWith"] },
            hasJS: { $in: ["JavaScript", "$LanguageHaveWorkedWith"] }
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
  { $match: { group: { $ne: "Other" } } },
  {
    $group: {
      _id: "$group",
      averageSalary: { $avg: "$salary" },
      count: { $sum: 1 }
    }
  },
  { $sort: { averageSalary: -1 } }
])
```
