/**
 * Created on 17-9-20.
 */
$.extend({
    textareaAutosize_dc:function(){
        var autoSizeFn=function(){}
        autoSizeFn.prototype={
            autosize:function(){
                var fontsize = $(this).css("font-size").replace("px","");//文字大小
                var fontrowcount = ($(this).width()/fontsize);//每行文字个数
                var textArray = $(this).val().split("\n");
                var currentEnterCount=textArray.length;//获取行数
                $(textArray).each(function(){
                    //检查每行文字量是否超过行容量 如果超过 贼需要加行, 超几行加几行
                   if(this.length>fontrowcount){
                       currentEnterCount+=this.length/fontrowcount;
                   }
                });
                var lineHeight=Number($(this).css("line-height").replace("px",""));
                $(this).height( lineHeight*(currentEnterCount+1));
            },addEvent:function(){
                //注册事件监听
                var self=this;
                 $("textarea").on("keyup",function(e){
                        self.autosize.call(this);
                 });
            },initAllHeight:function(){
                //初始化所有高度
                var self=this;
                 $("textarea").each(function(){
                     self.autosize.call(this);
                 });
            }
            ,init:function(){
                this.addEvent();
                this.initAllHeight();
            }
        }
       new autoSizeFn().init();
    }
}).fn.extend({
    textareaAutosize_dc:function(){
       var domSelf = this;
       var autoSizeFn=function(domSelf){
           this.domSelf=domSelf;
       }
        autoSizeFn.prototype={
            autosize:function(){
                var fontsize = $(this).css("font-size").replace("px","");//文字大小
                var fontrowcount = ($(this).width()/fontsize);//每行文字个数
                var textArray = $(this).val().split("\n");
                var currentEnterCount=textArray.length;//获取行数
                $(textArray).each(function(){
                    //检查每行文字量是否超过行容量 如果超过 贼需要加行, 超几行加几行
                   if(this.length>fontrowcount){
                       currentEnterCount+=this.length/fontrowcount;
                   }
                });
                var lineHeight=Number($(this).css("line-height").replace("px",""));
                $(this).height( lineHeight*(currentEnterCount+1));
            },addEvent:function(){
                //注册事件监听
                var self=this;
                 $(this.domSelf).on("keyup",function(e){
                        self.autosize.call(this);
                 });
            },initHeight:function(){
                var self=this;
                //初始化所有高度
                $(this.domSelf).each(function(){
                     self.autosize.call(this);
                 });
            }
            ,init:function(){
                this.addEvent();
                this.initHeight();
            }
        }
       new autoSizeFn(domSelf).init();
    }
});
//调用自动高度
//$.textareaAutosize_dc();//应用到所有textarea中
$('textarea').textareaAutosize_dc();//应用到指定的textarea中