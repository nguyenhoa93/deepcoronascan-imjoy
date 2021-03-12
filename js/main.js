const LOGOUT_URL = "/"
class Client {
  constructor(baseURL){
    this.baseURL = baseURL
    this.accessToken = null
  }
  async makeRequest(url, method, json){
    if(!this.accessToken) {
      await this.login()
    }
    if(!url.startsWith('http') && !url.startsWith('/')) url = this.baseURL + '/' + url;
    const headers = {'Authorization': `Bearer ${this.accessToken}`}
    let body = undefined
    if(json){
        headers['Content-Type'] = 'application/json'
        body = JSON.stringify(json)
    }
    const response = await fetch(url, {
      method,
      headers,
      body
    })
    const data = await response.json()
    if(data.success){
      return data.result
    }
    else{
      throw new Error(data.detail || data.error)
    }
  }
  async login(){
    const auth0 = await createAuth0Client({
      domain: 'imjoy.eu.auth0.com',
      client_id: 'ofsvx6A7LdMhG0hklr5JCAEawLv4Pyse'
    })
    await auth0.loginWithPopup({audience: 'https://imjoy.eu.auth0.com/api/v2/'});
    //logged in. you can get the user profile like this:
    const user = await auth0.getUser({audience: 'https://imjoy.eu.auth0.com/api/v2/'});
    this.isAdmin = false;
    if(user){
      if(!user.email_verified){
        window.alert(`Please verify your email (${user.email}) by clicking the link sent from Auth0.`)
        return
      }
      this.userInfo = user;
      if(user['https://api.imjoy.io/roles'].includes('admin'))
        this.isAdmin = true
      console.log(user);
    }
    this.auth0 = auth0;
    this.accessToken = await auth0.getTokenSilently({audience: 'https://imjoy.eu.auth0.com/api/v2/'});
  }
  async logout(){
    if(!this.auth0) {
      window.showMessage("You haven't logged in.")
      return;
    }
    await this.auth0.logout({returnTo: LOGOUT_URL});
  }
  async get(url){
    return this.makeRequest(url, 'GET')
  }
  async put(url, json){
    return this.makeRequest(url, 'PUT', json)
  }
  async post(url, json){
    return this.makeRequest(url, 'POST', json)
  }
  async delete(url){
    return this.makeRequest(url, 'DELETE')
  }
}

const app = new Vue({
  el: '#app',
  data: {
    client: null,
    tasks: null,
    baseUrl: 'https://ai.pasteur.fr',
    isAuthenticated: false
  },
  methods: {
    async login(){
    //   this.$vs.loading()
      try{
        this.client = new Client(this.baseUrl)
        this.tasks = await this.client.get(`${this.baseUrl}/tasks`)
        console.log("Client: ", this.client)
        console.log("Tasks: ", this.tasks)
        if (this.client.accessToken) {
          $("#logout-but").show()
          $("#avatar-img").show()
          $("#avatar-img").text(this.client.userInfo.name.charAt(0))
        //   if ("deepcoronascan" in this.tasks) {
        //     $("#eval-cam").show()
        //   }
        //   const all_samples = this.client.get(`${this.baseUrl}/task/deepcoronascan/sample/dnasample1`)
        //   console.log(all_samples)
        }
      }
      catch(e){
        window.alert(`Failed to connect to the backend server, error: ${e}`)
      }
    //   finally{
    //     this.$vs.loading.close()
    //   }
    },

    logout(){
      this.client.logout()
      this.client = null
      $("#eval-cam").hide()
      $("#authen-layout").hide()
      $("#disclaimer-layout").show()
    },

    goToPublic(){
      $("#disclaimer-layout").hide()
      $("#public-layout").show()
    },

    goBackDisclaimer(){
      $("#public-layout").hide()
      $("#disclaimer-layout").show()
    },

    goToAuthen(){
      $("#disclaimer-layout").hide()
      $("#authen-layout").show()
    },

    async view3D(){
      window.open("https://kitware.github.io/itk-vtk-viewer/app/?fileToLoad=https://data.kitware.com/api/v1/file/564a65d58d777f7522dbfb61/download/data.nrrd", "_blank")
    }
  }
})