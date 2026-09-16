import {svg,fmt} from './common.js';
let map;
const FAIXAS=[[40000,'#46bb70','Baixa'],[70000,'#f4c342','Moderada'],[100000,'#ff962d','Alta'],[Infinity,'#ef3f43','Muito alta']];
const faixa=pop=>FAIXAS.find(f=>pop<f[0]);

export function territory(){return `<div class="territory-layout"><section class="panel map-panel"><div class="panel-title"><div><h2>Mapa oficial das APGs</h2><p>17 Áreas de Planejamento e Gestão — camada “Histórico de População por APG”, Prefeitura de Campinas.</p></div><button class="select-look" id="reset-map">Ver Campinas inteira</button></div><div id="map" aria-label="Mapa das APGs de Campinas"><div class="map-fallback">Carregando mapa territorial…</div></div><div class="map-legend"><b>População 2022</b>${FAIXAS.map(([,c,l],i)=>`<span><i style="background:${c}"></i>${l}${['até 40 mil','40–70 mil','70–100 mil','acima de 100 mil'][i]?` · ${['até 40 mil','40–70 mil','70–100 mil','acima de 100 mil'][i]}`:''}</span>`).join('')}</div></section><aside class="panel apg-detail"><span class="eyebrow">APG SELECIONADA</span><h2>Selecione uma APG</h2><p>Clique em uma região no mapa para abrir os detalhes territoriais.</p><div class="empty-map">${svg('map')}<b>Nenhuma APG selecionada.</b><span>Clique em uma região do mapa para visualizar dados, indicadores e recomendações para esta APG.</span><span class="map-hint"></span></div></aside></div>`}

territory.mount=async()=>{
  if(!window.L)return;
  // ponytail: sem tilelayer - o basemap so trazia cidades vizinhas e rodovias; o recorte sao as APGs.
  map=L.map('map',{zoomControl:true,attributionControl:false,scrollWheelZoom:false});
  try{
    const data=await fetch('./apg.geojson').then(r=>r.json());
    const layer=L.geoJSON(data,{
      style:f=>({color:'#fff',weight:2,fillColor:faixa(f.properties?.POP_2022)[1],fillOpacity:.88}),
      onEachFeature:(f,l)=>{
        const nome=f.properties?.APG||f.properties?.nome||'APG';
        l.bindTooltip(String(nome).replace(/^APG\s*/i,''),{permanent:true,direction:'center',className:'apg-label'});
        l.on('click',()=>{showAPG(f.properties);map.fitBounds(l.getBounds(),{padding:[40,40]})});
        l.on('mouseover',()=>l.setStyle({weight:3,fillOpacity:1}));
        l.on('mouseout',()=>l.setStyle({weight:2,fillOpacity:.88}));
      }
    }).addTo(map);
    document.querySelector('.map-fallback')?.remove();
    const b=layer.getBounds();
    map.fitBounds(b,{padding:[24,24]});
    map.setMaxBounds(b.pad(.25)).setMinZoom(map.getZoom()-1);
    document.querySelector('#reset-map').onclick=()=>map.fitBounds(b,{padding:[24,24]});
    const top2=data.features.map(f=>f.properties).sort((a,z)=>z.POP_2022-a.POP_2022).slice(0,2);
    const hint=document.querySelector('.map-hint');
    if(hint)hint.textContent=`Maior população total: ${top2.map(t=>`${t.APG} (${fmt(t.POP_2022)})`).join(' e ')}.`;
  }catch{document.querySelector('.map-fallback').textContent='Não foi possível carregar a camada das APGs.'}
};

function showAPG(p){
  const nome=String(p.APG||p.nome||'APG').replace(/^APG\s*/i,''), pop=p.POP_2022, f=faixa(pop);
  document.querySelector('.apg-detail').innerHTML=`<span class="eyebrow">APG SELECIONADA</span><h2>${nome}</h2><p>População oficial (Prefeitura de Campinas); demais indicadores são ilustrativos.</p><div class="apg-stats"><div><small>População total 2022</small><b>${fmt(pop)}</b></div><div><small>População 60+ (est. 24%)</small><b>${fmt(Math.round(pop*.24))}</b></div><div><small>Pressão territorial</small><b style="color:${f[1]}">${f[2]}</b></div><div><small>População 2010</small><b>${fmt(p.POP_2010)}</b></div></div><div class="stack"><div class="insight"><div><b>Recomendação</b><p>Priorizar planejamento de cuidado e atenção domiciliar proporcional ao porte da APG.</p></div></div></div>`;
}
