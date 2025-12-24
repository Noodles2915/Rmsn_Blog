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
        // Tab 支持：在 textarea 中插入制表符而不是切换焦点；支持缩进/反缩进选中多行
        ta.addEventListener('keydown', function(e){
            if (e.key === 'Tab'){
                e.preventDefault();
                var start = ta.selectionStart, end = ta.selectionEnd;
                var val = ta.value;
                // 如果选择多行，则对每一行进行缩进或反缩进
                var selected = val.slice(start, end);
                if (selected.indexOf('\n') !== -1){
                    var linesStart = val.lastIndexOf('\n', start - 1) + 1;
                    var linesEnd = val.indexOf('\n', end);
                    if (linesEnd === -1) linesEnd = val.length;
                    var block = val.slice(linesStart, linesEnd);
                    if (e.shiftKey){
                        // 反缩进：移除每行首个制表符或四个空格
                        var newBlock = block.split('\n').map(function(line){
                            if (line.startsWith('\t')) return line.slice(1);
                            if (line.startsWith('    ')) return line.slice(4);
                            return line.replace(/^\s{0,1}/, '');
                        }).join('\n');
                        ta.value = val.slice(0, linesStart) + newBlock + val.slice(linesEnd);
                        // 重新设置选区覆盖原来行
                        ta.setSelectionRange(linesStart, linesStart + newBlock.length);
                    } else {
                        // 缩进：在每行前加一个制表符
                        var newBlock = block.split('\n').map(function(line){ return '\t' + line; }).join('\n');
                        ta.value = val.slice(0, linesStart) + newBlock + val.slice(linesEnd);
                        ta.setSelectionRange(linesStart, linesStart + newBlock.length);
                    }
                } else {
                    // 单行或无选中：在光标处插入制表符
                    var before = val.slice(0, start);
                    var after = val.slice(end);
                    var newPos = start + 1;
                    ta.value = before + '\t' + after;
                    ta.setSelectionRange(newPos, newPos);
                }
                triggerInput(ta);
                render();
            }
        });
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
                                btn.classList.remove('active');
                                btn.setAttribute('aria-pressed','false');
                                // remove container-level preview active state
                                if (container && container.classList) container.classList.remove('preview-active');
                                // remove button-level preview active marker
                                btn.classList.remove('preview-active-btn');
                            } else {
                                preview.classList.remove('hidden'); preview.classList.add('visible');
                                // hide raw markdown so rendered HTML shows through
                                ta.style.color = 'transparent';
                                render();
                                btn.classList.add('active');
                                btn.setAttribute('aria-pressed','true');
                                // mark container as preview-active for CSS hooks
                                if (container && container.classList) container.classList.add('preview-active');
                                // mark button as preview-active as a fallback
                                btn.classList.add('preview-active-btn');
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
                        case 'code': insertAroundSelection(ta,'```\n','\n```'); break;
                        case 'link': insertAroundSelection(ta,'[','](http://)'); break;
                        case 'image': insertAroundSelection(ta,'![](','') ; break;
                        default: break;
                    }
                });
                btn.dataset.bound = '1';
            });
                // sync preview button state on init
                var previewToggle = toolbar.querySelector('[data-action="preview-toggle"]');
                if (previewToggle){
                    if (preview && preview.classList.contains('visible')){
                        previewToggle.classList.add('active');
                        previewToggle.setAttribute('aria-pressed','true');
                        if (container && container.classList) container.classList.add('preview-active');
                        previewToggle.classList.add('preview-active-btn');
                    } else {
                        previewToggle.classList.remove('active');
                        previewToggle.setAttribute('aria-pressed','false');
                        if (container && container.classList) container.classList.remove('preview-active');
                        previewToggle.classList.remove('preview-active-btn');
                    }
                }
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
