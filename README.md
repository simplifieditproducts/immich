Steps to run development server on a Unix-based computer:

1) Clone this repo: `git clone https://github.com/simplifieditproducts/immich.git`
2) Navigate to project root directory: `cd immich`
2) Create the necessary `.env` file: `cp docker/example.env docker/.env`
3) Start the dev server using the provided Makefile: `make dev`
4) Access the instance in your web browser by using `http://localhost:3000` or `http://your-machine-ip:3000`

Official instructions [here](https://immich.app/docs/developer/setup).
