from app import App
from triangle import Triangle


def main():
    app = App()
    triangle = Triangle("./triangle/triangle.vert", "./triangle/triangle.frag")

    app.add_shape(triangle)

    app.run()


if __name__ == "__main__":
    main()
