/**
 * Created by qitan on 17-12-12.
 */

<!-- 展示样式 -->
function changeDisplay(index){
  if (index === 1) {
      {
          //document.getElementById("show_col").style.display = "";
          //document.getElementById("show_table").style.display = "none";
          $("#show_col").css("display", "");
          $("#show_table").css("display", "none");
      }
  } else if (index === 2) {
      {
          $("#show_col").css("display", "none");
          $("#show_table").css("display", "");
      }
  }
}
<!-- /展示样式 -->