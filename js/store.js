var Store = {};

Store.start = function(){
	$(document).ready(function() {
		Store.loadCategories();
		Store.loadStoreName();/*adding store name request*/
	});
};

Store.loadStoreName=function(){ /*adding function to request the store name*/
    $.get("/store_name", function(result){
        if (result["STATUS"] == "ERROR"){
			alert(result["MSG"]);
		}else{
		    var store_n=result["STORE"];
		    console.log(result);
		    console.log(store_n);
		    var nameHolder=$('#store-name');
		    nameHolder.empty();
		    nameHolder.text(store_n);
		    var e_mail=store_n+"@"+store_n+".com";
		    $(".buy form input[name='business']").val(e_mail);
		}
    },"json")
}

Store.loadCategories = function(){
	$.get("/categories",function(result){
			if (result["STATUS"] == "ERROR"){
				alert(result["MSG"]);
			}else{
				var categories = result["CATEGORIES"];
				var categoriesHolder = $("#categories");
				categoriesHolder.empty();
				for (i in categories){
					var categoryBtn = $("<nav />").addClass("nav-btn clickable").text(categories[i].name);
					categoryBtn.attr("id","cat-" + categories[i].id);
					categoryBtn.click(function(e){
						Store.loadProducts($(this).attr("id"));
					});
					categoriesHolder.append(categoryBtn)
				}
				$("#page").addClass("ready");
				var firstCategory = $("#categories .nav-btn").attr("id");
				Store.loadProducts(firstCategory);
			}
		},"json");
};

Store.loadProducts = function(category){
	var categoryID = category.replace("cat-","");
	$.get("/category/" + categoryID + "/products",function(result){
		$("#content").empty();
		for( i in result["PRODUCTS"]){
			var productObj = result["PRODUCTS"][i];
			var product = $("#templates .product").clone();
			product.find(".img").css("background-image","url('"+ productObj.img_url +"')");
			product.find(".title").text(productObj.title);
			product.find(".desc").text(productObj.description);
			product.find(".price").text("$" + productObj.price);
			product.find("form input[name='item_name']").val(productObj.title);
			product.find("form input[name='item_number']").val(productObj.id);
			product.find("form input[name='amount']").val(productObj.price);
			if (productObj.favorite){
				product.addClass("favorite");
			}
			$("#content").append(product);
		}
	},"json");
};
Store.start();

