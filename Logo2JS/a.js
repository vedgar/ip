var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
for (var r1 = 0; r1 < 46; r1 ++)
{
for (var r2 = 0; r2 < 4; r2 ++)
{
to.apply(ctx, [x-=Math.sin(h)*150, y-=Math.cos(h)*150]);
h += 1.5533430342749532;
}
h += 1.6231562043547265;
}
ctx.stroke();
