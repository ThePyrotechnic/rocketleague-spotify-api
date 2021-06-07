window.onload = () => {
	let codeBox = document.getElementById("code-box")

  let params = new URLSearchParams(document.location.search.substring(1))
  let code = params.get("code")
  codeBox.value = code ? code : "No code in URL!"

  codeBox.onclick = (event) => {
  	event.target.select()
    document.execCommand("copy")

    event.preventDefault()
  }
}
