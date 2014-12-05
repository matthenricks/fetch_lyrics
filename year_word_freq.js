var map = function() { emit( {"word": , "year": this.year}, {"count": 1}) };

var reduce = function(key, values) {
  var count = 0;

  values.forEach(function(v) {
    count += v['count'];
  });

  return {"count": count};
}

db.songs.mapReduce( map, reduce, { out: "songs_temp" } );



Input: (word_stem, (year, count))
Output: mean

var reduce = function(word, values) {
	year, count = values
	count_avg = Array.avg(count)

	return {"average": count_avg}
}