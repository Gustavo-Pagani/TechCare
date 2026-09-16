import {kpis,chart,insight,nums,fmt,val} from './common.js';
// ponytail: a faixa era literal ('2022 -> 2050 / +61,9%'); agora sai de nums, como o grafico.
// Leitura do cenario: tudo derivado de `nums`, a mesma fonte dos KPIs.
// O painel antes trazia tres frases fixas que nao mudavam com o ano.
// Leitura do cenario: so razoes e diferencas. Magnitudes ja estao nos KPIs e na faixa de
// crescimento logo acima - repeti-las aqui era o que fazia o painel parecer eco da tela.
const p1=x=>x.toFixed(1).replace('.',',');
const share80=x=>val(x[1])/val(x[0])*100;          // 80+ como % dos 60+
function leitura(year){const b=nums[2022],n=nums[year];
  return Number(year)===2022?[
    ['chart','ESTRUTURA',`1 em cada ${Math.round(100/share80(b))} idosos já tem 80 anos ou mais (${p1(share80(b))}%).`,'mint'],
    ['home','COBERTURA',`A demanda estimada de SAD equivale a ${p1(val(b[2])/val(b[0])*100)}% da população 60+.`,'green'],
    ['target','ANO BASE','Ponto de referência: as variações dos cenários 2030–2050 são medidas a partir daqui.','blue']]:[
    ['chart','ESTRUTURA',`Os 80+ chegam a ${p1(share80(n))}% da população idosa — ${p1(share80(n)-share80(b))} pontos acima de hoje.`,'mint'],
    ['elder','PRESSÃO',`Mais ${fmt(val(n[1])-val(b[1]))} pessoas com 80+ que hoje — o grupo que mais pressiona ILPI e cuidado contínuo.`,'blue'],
    ['home','ESFORÇO',`Mais ${fmt(val(n[2])-val(b[2]))} atendimentos SAD que a estimativa atual.`,'green']]}
function growth(year){const base=val(nums[2022][0]);if(Number(year)===2022)return `<b>↗　Ano base · 2022<br><strong>${nums[2022][0]}</strong></b><b>pessoas<br><small>60+</small></b>`;const d=val(nums[year][0])-base;return `<b>↗　Crescimento 2022 → ${year}<br><strong>+${(d/base*100).toFixed(1).replace('.',',')}%</strong></b><b>+${fmt(d)}<br><small>pessoas</small></b>`}
export function overview({year}){return `${kpis(year)}<div class="two-cols overview-main"><section class="panel"><h2>Evolução da população idosa</h2><p>Projeção da população com 60+ e 80+ anos em Campinas</p><div class="double-chart">${chart('População 60+','var(--teal)',0,year)}${chart('População 80+','var(--blue)',1,year)}</div><div class="growth">${growth(year)}</div></section><section class="panel scenario"><h2>Leitura do cenário</h2><p>O que os números de ${year} indicam para o planejamento.</p><div class="stack">${leitura(year).map(x=>insight(...x)).join('')}</div></section></div>`}
