var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
to = ctx.moveTo;
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
