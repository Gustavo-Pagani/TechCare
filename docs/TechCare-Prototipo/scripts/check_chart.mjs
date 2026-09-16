// Check minimo do chart(): escala ancorada, truncamento por ano e series distintas.
// Rodar: node scripts/check_chart.mjs
import assert from 'node:assert/strict';
import {chart,nums,val,fmt,YEARS} from '../pages/common.js';

const cys=svg=>[...svg.matchAll(/<circle cx="(\d+)" cy="([\d.]+)"/g)].map(m=>[+m[1],+m[2]]);

// truncamento: um ponto por ano ja alcancado
YEARS.forEach((y,i)=>assert.equal(cys(chart('','red',0,y)).length,i+1,`${y} deveria ter ${i+1} ponto(s)`));

// escala ancorada no intervalo completo 2022->2050, nao no trecho visivel:
// 2022 fica sempre em 137 e 2050 em 50, nas duas series.
for(const serie of [0,1]){
  assert.equal(cys(chart('','red',serie,2022))[0][1],137,'2022 deve ancorar em y=137');
  assert.equal(cys(chart('','red',serie,2050))[3][1],50,'2050 deve ancorar em y=50');
  // o ponto de 2030 nao muda de lugar quando o ano avanca (dominio fixo)
  assert.equal(cys(chart('','red',serie,2030))[1][1],cys(chart('','red',serie,2050))[1][1]);
}

// regressao do "ponto solto": os anos ainda nao alcancados aparecem tracejados,
// entao o grafico nunca fica vazio. Solidos + fantasmas sempre fecham os 4 anos.
const ghosts=svg=>(svg.match(/<circle class="ghost"/g)||[]).length;
YEARS.forEach((y,i)=>{
  const svg=chart('','red',0,y);
  assert.equal(ghosts(svg),3-i,`${y} deveria ter ${3-i} ponto(s) futuro(s)`);
  assert.equal(cys(svg).length+ghosts(svg),4,'solidos + fantasmas devem cobrir os 4 anos');
  assert.match(svg,/stroke-dasharray/,'a projecao completa deve estar sempre desenhada');
});

// regressao do bug original: 60+ e 80+ desenhavam exatamente a mesma curva
assert.notEqual(cys(chart('','red',0,2050))[2][1],cys(chart('','red',1,2050))[2][1],
  '60+ e 80+ nao podem compartilhar a mesma geometria');

// anos ainda nao alcancados saem esmaecidos no eixo
assert.equal((chart('','red',0,2030).match(/class="dim"/g)||[]).length,2);

// faixa de crescimento (mesma conta usada em overview.js)
const base=val(nums[2022][0]);
const growth=y=>{const d=val(nums[y][0])-base;return[`+${(d/base*100).toFixed(1).replace('.',',')}%`,`+${fmt(d)}`]};
assert.deepEqual(growth(2030),['+16,6%','+45.464']);
assert.deepEqual(growth(2050),['+61,9%','+169.222']);  // confere com o texto fixo antigo

console.log('ok');
