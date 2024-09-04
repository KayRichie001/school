//add hovered class to selected list item
let list = document.querySelectorAll(".navigation li");

function activeLink(){
    list.forEach((item)=>{
        item.classList.remove("hovered");
    });
    this.classList.add("hovered");
}

list.forEach(item => item.addEventListener("mouseover",activeLink));

//menu Toggle
let toggle = document.querySelector(".Menu");
let navigation = document.querySelector(".navigation");
let main = document.querySelector(".main");


toggle.addEventListener("click", function() {
    navigation.classList.add("active");
    main.classList.toggle("active");
});
