var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2;
var y = canvas.height / 2;
var h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
for (var r1 = 0; r1 < 3; r1 ++)
{
for (var r2 = 0; r2 < 18; r2 ++)
{
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
h += 1.7453292519943295;
}
h += 2.0943951023931953;
to = ctx.moveTo;
to.apply(ctx, [x-=Math.sin(h)*150, y-=Math.cos(h)*150]);
to = ctx.lineTo;
}
ctx.stroke();
