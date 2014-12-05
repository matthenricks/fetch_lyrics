var map = function() { emit( {"word": , "year": this.year}, {"count": 1}) };

var reduce = function(key, values) {
  var count = 0;

  values.forEach(function(v) {
    count += v['count'];
  });

  return {"count": count};
}

db.songs.mapReduce( map, reduce, { out: "songs_temp" } );
