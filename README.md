# python-image-processing

## Important

Copy your licenced copy of *CurveLab-2.1.3.tar.gz* inside the *.devcontainer* folder before building!

## Install python requirements

```bash
pip3 install -r requirements.txt
```
## Information
These scripts can import RAW files which container HDR images. The format is:

```C++
struct Vector3 
{
    float r, g, b;
}
struct RawFormat
{
    int width;
    int height;
    std::vector<Vector3> // length width*height
}
```
## Other

Happy coding!
