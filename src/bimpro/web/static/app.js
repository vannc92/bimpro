// Bảng lưới: thêm, xóa, đổi thứ tự dòng; đánh lại chỉ số tên trường trước khi gửi
function renumber(table){
  const name=table.dataset.name;
  table.querySelectorAll('tbody tr').forEach((tr,i)=>{
    tr.querySelector('.handle').textContent=i+1;
    tr.querySelectorAll('[name]').forEach(el=>{el.name=el.name.replace(new RegExp('^g\\.'+name+'\\.(\\d+|__i__)\\.'),'g.'+name+'.'+i+'.')});
  });
}
document.addEventListener('click',e=>{
  const t=e.target;
  if(t.matches('button.add')){
    const table=document.querySelector('table.grid[data-name="'+t.dataset.for+'"]');
    const row=table.querySelector('tr.tplrow').cloneNode(true);row.hidden=false;row.classList.remove('tplrow');
    table.querySelector('tbody').appendChild(row);renumber(table);row.querySelector('input,textarea')?.focus();
  }else if(t.matches('.grid button.x')){const table=t.closest('table');t.closest('tr').remove();renumber(table);}
  else if(t.matches('.grid button.up')){const tr=t.closest('tr');if(tr.previousElementSibling){tr.parentNode.insertBefore(tr,tr.previousElementSibling);renumber(t.closest('table'));}}
});
document.getElementById('gform')?.addEventListener('submit',()=>{
  document.querySelectorAll('tr.tplrow').forEach(r=>r.remove());
  document.querySelectorAll('table.grid').forEach(renumber);
});
// Ghi nhớ ô đang nhập để chép trích dẫn vào
let lastField=null;
document.addEventListener('focusin',e=>{if(e.target.matches('#gform input:not([type=checkbox]):not([type=hidden]),#gform textarea'))lastField=e.target;});
// Tra cứu hồ sơ đầu vào
const sform=document.getElementById('sform');
function esc(s){return s.replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function search(q){
  const box=document.getElementById('hits');box.innerHTML='<p class="muted">Đang tìm…</p>';
  const r=await fetch('/p/'+sform.dataset.pid+'/search?q='+encodeURIComponent(q));const hits=await r.json();
  if(!hits.length){box.innerHTML='<p class="muted">Không có kết quả.</p>';return;}
  box.innerHTML='';
  hits.forEach(h=>{
    const d=document.createElement('div');d.className='hit';
    d.innerHTML='<div class="src">'+esc(h.name)+' · tr. '+h.page+'</div><div>'+esc(h.snippet).replace(/\[\[/g,'<mark>').replace(/\]\]/g,'</mark>')+'</div>'+
      '<div class="acts"><button type="button" class="ghost cp">Chép vào ô</button><button type="button" class="ghost op">Mở tệp</button></div>';
    d.querySelector('.cp').onclick=()=>{
      const text=h.snippet.replace(/\[\[|\]\]/g,'').replace(/^ … | … $/g,'');
      if(!lastField){navigator.clipboard?.writeText(text);alert('Chưa chọn ô cần điền. Đã chép vào bộ nhớ tạm.');return;}
      const s=lastField.selectionStart??lastField.value.length;
      lastField.value=lastField.value.slice(0,s)+text+lastField.value.slice(lastField.selectionEnd??s);
      const cite=lastField.closest('.field')?.querySelector('input[name^="cite."]');
      if(cite)cite.value=h.name+', tr. '+h.page;
      lastField.focus();
    };
    d.querySelector('.op').onclick=()=>openFile(h.file);
    box.appendChild(d);
  });
}
async function openFile(path){
  const fd=new FormData();fd.append('path',path);
  const r=await fetch('/p/'+sform.dataset.pid+'/open',{method:'POST',body:fd});if(!r.ok)alert('Không mở được tệp');
}
if(sform){
  sform.addEventListener('submit',e=>{e.preventDefault();const q=document.getElementById('q').value.trim();if(q)search(q);});
  document.querySelectorAll('.kwb').forEach(b=>b.onclick=()=>{document.getElementById('q').value=b.textContent;search(b.textContent);});
}
document.querySelectorAll('a.open').forEach(a=>a.onclick=e=>{e.preventDefault();openFile(a.dataset.path)});
