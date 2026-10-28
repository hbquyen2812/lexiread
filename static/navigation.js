/* The public name may change; keep existing preference keys and user data compatible. */
(() => {
  'use strict';
  const sidebar=document.querySelector('.sidebar');
  if(!sidebar)return;
  const desktop=document.querySelector('[data-sidebar-toggle]');
  const mobile=document.querySelector('.mobile-menu-toggle');
  const media=window.matchMedia('(min-width: 881px)');
  const labels={vi:['Mở menu','Ẩn menu'],en:['Open menu','Hide menu'],fr:['Ouvrir le menu','Masquer le menu'],zh:['打开菜单','收起菜单']};
  let collapsed=false;
  try{collapsed=localStorage.getItem('lexiread.sidebar.collapsed')==='true';}catch{}
  function render(){
    const hidden=media.matches&&collapsed;
    document.body.classList.toggle('nav-collapsed',hidden);
    sidebar.inert=hidden;
    if(hidden)sidebar.setAttribute('aria-hidden','true');else sidebar.removeAttribute('aria-hidden');
    const text=labels[window.LexiI18n?.language]||labels.vi;
    if(desktop){desktop.setAttribute('aria-expanded',String(!collapsed));desktop.setAttribute('aria-label',text[collapsed?0:1]);desktop.title=text[collapsed?0:1];}
    if(mobile)mobile.setAttribute('aria-expanded',String(sidebar.classList.contains('menu-open')));
  }
  function closeMobile(){sidebar.classList.remove('menu-open');render();}
  function toggle(){
    if(media.matches){collapsed=!collapsed;try{localStorage.setItem('lexiread.sidebar.collapsed',String(collapsed));}catch{}}
    else sidebar.classList.toggle('menu-open');
    render();
  }
  desktop?.addEventListener('click',toggle);
  document.addEventListener('keydown',event=>{
    if(event.key!=='Escape')return;
    if(media.matches&&!collapsed&&sidebar.contains(document.activeElement)){collapsed=true;try{localStorage.setItem('lexiread.sidebar.collapsed','true');}catch{}render();desktop?.focus();}
    else if(!media.matches&&sidebar.classList.contains('menu-open')){closeMobile();mobile?.focus();}
  });
  media.addEventListener('change',closeMobile);
  document.addEventListener('lexiread:language',render);
  window.LexiNavigation={toggle,closeMobile};
  render();
})();
