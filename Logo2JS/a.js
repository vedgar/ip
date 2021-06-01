var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
for (var r1 = 0; r1 < 10; r1 ++) 
{
for (var r2 = 0; r2 < 5; r2 ++) 
{
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
h += 1.2566370614359172;
}
h += 1.2566370614359172;
}
ctx.stroke();