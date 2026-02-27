# 3. Iskustvo po veličini kompanije i top jezici

## Opis upita
Izračunajte prosečno radno iskustvo (YearsCodePro) za developere u kompanijama sa različitim brojem zaposlenih (OrgSize). Za svaku veličinu kompanije prikažite i tri najpopularnija programska jezika među ispitaniсima.

## Query

```javascript
db.getCollection('developers').aggregate([
  {
    
    $match: {
      "OrgSize": { $ne: NaN },
      "YearsCodePro": { $ne: NaN },
      "Age": { $ne: NaN, $ne: null }
    }
  },
  {
    // JOIN
    $lookup: {
      from: "technologies",
      localField: "ResponseId",
      foreignField: "ResponseId",
      as: "tech"
    }
  },
  { $unwind: "$tech" },
  {
    // UNWIND JEZIKA
    $unwind: "$tech.LanguageHaveWorkedWith"
  },
  {
    // PRVO GRUPISANJE po FIRMI JEZIKU I STAROSTI,  -- br ljudi i avg staz
    $group: {
      _id: {
        velicinaFirme: "$OrgSize",
        jezik: "$tech.LanguageHaveWorkedWith",
        starosnaGrupa: "$Age"
      },
      prosecnoIskustvo: { $avg: "$YearsCodePro" },
      brojPojavljivanjaKombinacije: { $sum: 1 }
    }
  },
  {
    // 5. SORTIRANJE za najcescu starosnu grupu posle cu first
    $sort: { "_id.velicinaFirme": 1, "brojPojavljivanjaKombinacije": -1 } //red sa najvise ljudi je sada na vrhu
  },
  {
    //  DRUGO GRUPISANJE - SAMO PO FIRMI
    $group: {
      _id: "$_id.velicinaFirme",
      prosecnoIskustvoUGrupi: { $avg: "$prosecnoIskustvo" }, // U TOJ FIRMI
      
      // $first uzme onu starosnu grupu koja se najvise puta pojavila
      najcescaStarosnaGrupa: { $first: "$_id.starosnaGrupa" },
      popularniJezici: {
        $push: {
          jezik: "$_id.jezik",
          korisnika: "$brojPojavljivanjaKombinacije"
        }
      }
    }
  },
  {
    $project: {
      _id: 0,
      velicinaKompanije: "$_id",
      stazProsek: { $round: ["$prosecnoIskustvoUGrupi", 1] },
      najcescaStarosnaGrupa: 1,
      top3Jezika: { $slice: ["$popularniJezici", 3] }
    }
  },
  {
    $sort: { "stazProsek": 1 }
  }
])
```