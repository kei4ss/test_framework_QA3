const { RequestManager } = require("../infraestructure/requestManager");

const rm = RequestManager.getInstance({
  baseURL: "https://fakestoreapi.com",
  headers: { "Test-Version": "2.1.0" },
  maxConcurrent: 5,
});

rm.setAuthToken("meu-token-jwt");

const userService = {
  api: RequestManager.getInstance(), 
  async listarUsuarios() {
    return this.api.get("/users");
  },

  async criarUsuario(dados) {
    return this.api.post("/users", dados);
  },
};

const productService = {
  api: RequestManager.getInstance(), 

  async listarProdutos() {
    return this.api.get("/products");
  },

  async atualizarProduto(id, dados) {
    return this.api.put(`/products/${id}`, dados);
  },
};


const orderService = {
  api: RequestManager.getInstance(), 
  async criarPedido(carrinho) {
    return this.api.post("/orders", carrinho);
  },

  async cancelarPedido(id) {
    return this.api.delete(`/orders/${id}`);
  },
};

console.log(
  "userService.api === productService.api?",
  userService.api === productService.api 
);

console.log(
  "productService.api === orderService.api?",
  productService.api === orderService.api 
);

console.log("Stats:", RequestManager.getInstance().getStats());

module.exports = { userService, productService, orderService };

