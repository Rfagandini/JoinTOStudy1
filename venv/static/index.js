function delete_booking(id) {
  fetch("/delete_booking", {
    method: "POST",
    body: JSON.stringify({ id: id })
  }).then((_res) => {
    window.location.href = "/";
  });
}