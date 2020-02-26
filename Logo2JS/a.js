var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
for (var r1 = 0; r1 < 8; r1 ++)
{
for (var r2 = 0; r2 < 8; r2 ++)
{
to.apply(ctx, [x-=Math.sin(h)*67, y-=Math.cos(h)*67]);
h += 0.7853981633974483;
}
h += 0.7853981633974483;
}
ctx.stroke();
