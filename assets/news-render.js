/* Renders window.SALSAL_NEWS into a container.
   salsalRenderNews(containerId, base, limit, featureFirst)
     base:  "" on the homepage, "../" one level deep
     limit: max items (0 or omit = all)
     featureFirst: true to render the newest item as a large featured card */
function salsalRenderNews(containerId, base, limit, featureFirst){
  var el=document.getElementById(containerId);
  if(!el || !window.SALSAL_NEWS){ return; }
  base = base || "";
  var items = window.SALSAL_NEWS.slice().sort(function(a,b){
    return a.date < b.date ? 1 : (a.date > b.date ? -1 : 0);
  });
  if(limit){ items = items.slice(0, limit); }
  var now = new Date();
  function fmt(d){
    var p = d.split("-");
    var dt = new Date(+p[0], +p[1]-1, +p[2]);
    return dt.toLocaleDateString("en-US", {month:"short", day:"numeric", year:"numeric"});
  }
  function isUpcoming(d){
    var p = d.split("-");
    return new Date(+p[0], +p[1]-1, +p[2]) > now;
  }
  function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }
  el.innerHTML = items.map(function(n, i){
    var up = isUpcoming(n.date);
    var tag = up ? "Upcoming" : (n.tag || "Update");
    var feat = (featureFirst && i === 0) ? " feat" : "";
    return '<a class="ncard'+feat+'" href="'+base+n.href+'">'+
      '<div class="nmeta"><span class="ntag'+(up?" up":"")+'">'+esc(tag)+'</span>'+
      '<span class="ndate">'+fmt(n.date)+'</span></div>'+
      '<h3>'+esc(n.title)+'</h3><p>'+esc(n.blurb)+'</p>'+
      '<span class="ngo">Read more &rsaquo;</span></a>';
  }).join("");
}
