import { shell } from './shared/shell.js';
import { pages } from './pages/index.js';
const root = document.querySelector('#app'); let current = 'reason'; let year = 2022;
function render() { root.innerHTML = shell({ current, year, content: pages[current]({ year }) }); pages[current].mount?.({ year }); document.querySelectorAll('[data-page]').forEach(b=>b.addEventListener('click',()=>{current=b.dataset.page;render()})); document.querySelectorAll('[data-year]').forEach(b=>b.addEventListener('click',()=>{year=Number(b.dataset.year);render()})); }
render();
