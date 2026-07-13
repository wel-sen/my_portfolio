const form = document.getElementById("contact-form");

form.addEventListener("submit", function (e) {

    e.preventDefault();

    emailjs.sendForm(
        "service_tfmemhl",
        "template_afgwagl",
        this
    )
    .then(() => {

        alert("Message sent successfully!");

        form.reset();

    })
    .catch((error) => {

        console.log(error);

        alert("Failed to send message.");

    });

});