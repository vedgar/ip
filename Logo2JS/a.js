var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
for (var r1 = 0; r1 < 12; r1 ++) {
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*55, y-=Math.cos(h)*55]);
to = ctx.lineTo
h += 0.5235987755982988;
for (var r2 = 0; r2 < 18; r2 ++) {
h += 0.3490658503988659;
for (var r3 = 0; r3 < 4; r3 ++) {
to.apply(ctx, [x-=Math.sin(h)*15, y-=Math.cos(h)*15]);
h += 1.5707963267948966;
}
}
}
ctx.stroke();