function setMode(student){document.body.classList.toggle('students',student);document.getElementById('guide').setAttribute('aria-pressed',String(!student));document.getElementById('sheets').setAttribute('aria-pressed',String(student));}
document.querySelectorAll('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode==='student')));
document.getElementById('print-all')?.addEventListener('click',()=>{document.body.classList.remove('print-single');window.print()});
document.querySelectorAll('[data-lesson]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.print-target').forEach(s=>s.classList.remove('print-target'));document.getElementById(b.dataset.lesson).classList.add('print-target');document.body.classList.add('print-single');window.print()}));
window.addEventListener('afterprint',()=>document.body.classList.remove('print-single'));
