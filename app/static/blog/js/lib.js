/**
 * Created by ysicing on 2017/3/12.
 * 生日快乐。按照惯例先立个flag
 * 嘿嘿嘿
 */
function getCookie(e){
    var t=null;
    if(document.cookie)for(var n=document.cookie.split(";"),o=0;o<n.length;o++){var a=$.trim(n[o]);if(a.substring(0,e.length+1)==e+"="){t=decodeURIComponent(a.substring(e.length+1));break}}return t
}

function deleteComment(e){
    return fetch("/api/comments/delete/"+e+"/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},credentials:"include"})
}
function createComment(e){
    return fetch("/api/comments/post/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},body:e,credentials:"include"})
}
function createArticle(e){
    return fetch("/api/articles/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},body:e,credentials:"include"})
}
function updateArticle(e,t){
    return fetch("/api/articles/"+e+"/",{method:"PUT",headers:{"X-CSRFToken":getCookie("csrftoken")},body:t,credentials:"include"})
}
function uploadFile(e){
    return fetch("/imgbox/api/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},body:e,credentials:"include"})
}
function fetchDouban(e){
    return fetch("/api/tools/douban/?douban_id="+e,{method:"GET",headers:{"X-CSRFToken":getCookie("csrftoken")},credentials:"include"})
}
function createMonitorTask(e){
    return fetch("/api/monitor/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},body:e,credentials:"include"})
}
function verifyMonitorTask(e){
    return fetch("/api/monitor/verify/",{method:"POST",headers:{"X-CSRFToken":getCookie("csrftoken")},body:e,credentials:"include"})
}
function sidebarCategory(){
    var e=$("#category");"none"==e.css("display")?e.fadeIn():e.fadeOut()
}
function sidebarLib(){
    var e=$("#lib");"none"==e.css("display")?e.fadeIn():e.fadeOut()
}
function sidebarAnalysis(){var e=$("#analysis");"none"==e.css("display")?e.fadeIn():e.fadeOut()}function sidebarLife(){var e=$("#life");"none"==e.css("display")?e.fadeIn():e.fadeOut()}function referredTo(e){var t=e.dataset.username,n=$("#comment-textarea");return n.val(n.val()+"@"+t+" "),n.focus(),!1}function commentUp(e){var t=$("#thumb-up-"+e.dataset.id);t.hasClass("red-text")?(t.addClass("grey-text"),t.removeClass("red-text")):(t.addClass("red-text"),t.removeClass("grey-text"));var n=$("#thumb-down-"+e.dataset.id);n.removeClass("red-text"),n.addClass("grey-text")}function commentDown(e){var t=$("#thumb-down-"+e.dataset.id);t.hasClass("red-text")?(t.removeClass("red-text"),t.addClass("grey-text")):(t.removeClass("grey-text"),t.addClass("red-text"));var n=$("#thumb-up-"+e.dataset.id);n.removeClass("red-text"),n.addClass("grey-text")}function initLineChart(e,t,n){var o=[];for(var a in t)o.push(t[a]);new Chart(e,{type:"line",data:{labels:Object.keys(t),datasets:[{label:n,data:o,backgroundColor:[randomColor({luminosity:"light",format:"rgba",alpha:.2})],borderColor:[randomColor({luminosity:"dark",format:"rgba"})],borderWidth:1}]}})}function beginCircleLoding(){$("#circle-loading").show()}function endCircleLoding(){$("#circle-loading").hide()}function prompt_warning(e,t){var n=$('<span class="red-text">'+e+"</span>");Materialize.toast(n,t)}function prompt_success(e,t){var n=$("<span>"+e+"</span>");Materialize.toast(n,t)}app={},app.modal={delete:{id:null,redirect:null}},$("#side-nav-menu").sideNav({edge:"left"}),$(document).ready(function(){$(".modal").modal({dismissible:!0,opacity:.5,in_duration:300,out_duration:200,starting_top:"4%",ending_top:"10%",ready:function(e,t){var n=t[0].dataset.id,o=t[0].dataset.redirect;n&&(app.modal.delete.id=n),o&&(app.modal.delete.redirect=o)},complete:function(){}})}),$(document).ready(function(){$("#modal-delete").find(".modal-confirm").click(function(){$("#modal-delete").modal("close"),beginCircleLoding(),deleteComment(app.modal.delete.id).then(function(e){endCircleLoding(),e.ok?(app.modal.delete.redirect?location.pathname=app.modal.delete.redirect:location.reload(),prompt_success("删除成功",3e3)):e.json().then(function(e){prompt_warning(e.detail||"删除失败",3e3)}),app.modal.delete.id=null,app.modal.delete.redirect=null})})});