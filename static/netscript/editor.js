(function(){
    function insertAroundSelection(textarea, before, after){
        var start = textarea.selectionStart, end = textarea.selectionEnd;
        var val = textarea.value;
        var selected = val.slice(start, end) || '';
        var newText = before + selected + after;
        textarea.value = val.slice(0, start) + newText + val.slice(end);
        // restore selection to inside inserted content
        var newStart = start + before.length;
        var newEnd = newStart + selected.length;
        textarea.setSelectionRange(newStart, newEnd);
        textarea.focus();
        triggerInput(textarea);
    }

    function triggerInput(ta){
        var ev = new Event('input', { bubbles: true });
        ta.dispatchEvent(ev);
    }

    function escapeHtml(s){ return s.replace(/[&<>"]+/g, function(m){ return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m])||m; }); }

    function initEditorContainer(container){
        if (!container) return;
        // find textarea inside container
        var ta = container.querySelector('textarea');
        if (!ta) return;
        if (ta.dataset.editorInited) return;
        ta.dataset.editorInited = '1';

        // find toolbar (may be before textarea)
        var toolbar = container.querySelector('.editor-toolbar');
        var preview = container.querySelector('.markdown-preview');
        var previewContent = container.querySelector('.preview-content');

        // ensure marked exists
        function render(){
            try{
                var md = ta.value || '';
                if (previewContent && window.marked){
                    previewContent.innerHTML = window.marked.parse(md);
                }
                // keep preview scroll in sync when content changes
                if (preview && ta){ preview.scrollTop = ta.scrollTop; }
            }catch(e){ /* ignore */ }
        }

        ta.addEventListener('input', render);
        // sync scroll position
        ta.addEventListener('scroll', function(){ if (preview) preview.scrollTop = ta.scrollTop; });
        
        // Initialize: if preview is hidden, ensure textarea text is visible
        if (preview && preview.classList.contains('hidden')){
            ta.style.color = '';
        }
        
        render();

        if (toolbar){
            toolbar.querySelectorAll('.tool').forEach(function(btn){
                if (btn.dataset.bound) return;
                btn.addEventListener('click', function(e){
                    var action = btn.getAttribute('data-action');
                    if (!action) return;
                    if (action === 'preview-toggle'){
                        if (!preview) return;
                        var isVisible = preview.classList.contains('visible');
                        if (isVisible){
                            preview.classList.remove('visible'); preview.classList.add('hidden');
                            // show raw markdown text
                            ta.style.color = '';
                        } else {
                            preview.classList.remove('hidden'); preview.classList.add('visible');
                            // hide raw markdown so rendered HTML shows through
                            ta.style.color = 'transparent';
                            render();
                        }
                        return;
                    }
                    switch(action){
                        case 'bold': insertAroundSelection(ta,'**','**'); break;
                        case 'italic': insertAroundSelection(ta,'*','*'); break;
                        case 'h1': insertAroundSelection(ta,'# ',''); break;
                        case 'h2': insertAroundSelection(ta,'## ',''); break;
                        case 'ul': insertAroundSelection(ta,'- ',''); break;
                        case 'ol': insertAroundSelection(ta,'1. ',''); break;
                        case 'quote': insertAroundSelection(ta,'> ',''); break;
                        case 'code': insertAroundSelection(ta,'``\n','\n```'); break;
                        case 'link': insertAroundSelection(ta,'[','](http://)'); break;
                        case 'image': insertAroundSelection(ta,'![](','') ; break;
                        default: break;
                    }
                });
                btn.dataset.bound = '1';
            });
        }
    }

    function initAll(root){
        (root || document).querySelectorAll('.markdown-editor-container').forEach(function(c){ initEditorContainer(c); });
        // also init for dynamically created reply forms which may not include container wrapper
        (root || document).querySelectorAll('form.reply-form-local').forEach(function(f){ initEditorContainer(f); });
    }

    // Observe for added nodes (reply forms added dynamically)
    var mo = new MutationObserver(function(muts){
        muts.forEach(function(m){
            m.addedNodes && m.addedNodes.forEach(function(node){
                if (node.nodeType !== 1) return;
                if (node.matches && node.matches('.reply-form-local')){
                    initEditorContainer(node);
                } else if (node.querySelectorAll && node.querySelectorAll('.markdown-editor-container').length){
                    initAll(node);
                }
            });
        });
    });
    if (document.body) mo.observe(document.body, { childList:true, subtree:true });

    document.addEventListener('DOMContentLoaded', function(){ initAll(); });

    // expose for manual init
    window.__rmsn_editor_init = initAll;
})();
