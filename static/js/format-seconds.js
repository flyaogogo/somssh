/**
 * Created by qitan on 17-12-27.
 */
/**
 * 格式化秒
 * @param   int     value   总秒数
 * @return  string  result  格式化后的字符串
 */
function formatSeconds(value) {
    var theTime = parseInt(value);// 需要转换的时间秒
    var theTime1 = 0;// 分
    var theTime2 = 0;// 小时
    var theTime3 = 0;// 天
    if(theTime > 60) {
        theTime1 = parseInt(theTime/60);
        theTime = parseInt(theTime%60);
        if(theTime1 > 60) {
            theTime2 = parseInt(theTime1/60);
            theTime1 = parseInt(theTime1%60);
            if(theTime2 > 24){
                //大于24小时
                theTime3 = parseInt(theTime2/24);
                theTime2 = parseInt(theTime2%24);
            }
        }
    }
    var result = '';
    //if(theTime > 0){
    if(theTime1 <= 0){
        //result = ""+parseInt(theTime)+"秒";
        result = "";
    }
    if(theTime1 > 0) {
        result = ""+parseInt(theTime1)+"分"+result;
    }
    if(theTime2 > 0) {
        result = ""+parseInt(theTime2)+"小时"+result;
    }
    if(theTime3 > 0) {
        result = ""+parseInt(theTime3)+"天"+result;
    }
    return result;
}

