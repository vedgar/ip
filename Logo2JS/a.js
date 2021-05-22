var canvas = document.getElementById('output');
var ctx = canvas.getContext('2d');
var x = canvas.width / 2, y = canvas.height / 2, h = 0;
var to = ctx.lineTo;
ctx.moveTo(x, y);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*-50, y-=Math.cos(h)*-50]);
h += -1.5707963267948966;
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
to = ctx.moveTo
h += 1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*-50, y-=Math.cos(h)*-50]);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
to = ctx.moveTo
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*35, y-=Math.cos(h)*35]);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*-25, y-=Math.cos(h)*-25]);
to = ctx.lineTo
h += -1.5707963267948966;
to.apply(ctx, [x-=Math.sin(h)*100, y-=Math.cos(h)*100]);
to = ctx.lineTo
h += -1.5707963267948966;
to = ctx.moveTo
to.apply(ctx, [x-=Math.sin(h)*-25, y-=Math.cos(h)*-25]);
to = ctx.lineTo
to.apply(ctx, [x-=Math.sin(h)*50, y-=Math.cos(h)*50]);
ctx.stroke();