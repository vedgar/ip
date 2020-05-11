var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
for (var r1 = 0; r1 < 9; r1 ++) {
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*80, y-=Math.cos(h)*80]);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*-80, y-=Math.cos(h)*-80]);
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*6, y-=Math.cos(h)*6]);
to = ctx.lineTo
for (var r2 = 0; r2 < 2; r2 ++) {
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*80, y-=Math.cos(h)*80]);
h += 1.5707963267948966;
}
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*56, y-=Math.cos(h)*56]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*80, y-=Math.cos(h)*80]);
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*-50, y-=Math.cos(h)*-50]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*-80, y-=Math.cos(h)*-80]);
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*40, y-=Math.cos(h)*40]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*20, y-=Math.cos(h)*20]);
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*-20, y-=Math.cos(h)*-20]);
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*-40, y-=Math.cos(h)*-40]);
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*6, y-=Math.cos(h)*6]);
to = ctx.lineTo
for (var r3 = 0; r3 < 2; r3 ++) {
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*80, y-=Math.cos(h)*80]);
h += 1.5707963267948966;
}
to = ctx.moveTo
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*10, y-=Math.cos(h)*10]);
h += 1.0471975511965976;
}
ctx.stroke();