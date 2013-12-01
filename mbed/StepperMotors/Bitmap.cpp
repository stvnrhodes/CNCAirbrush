#include "Bitmap.h"
#define OFFSET_LOCATION 0x0a
#define WIDTH_LOCATION 0x12
#define HEIGHT_LOCATION 0x16

bool Bitmap::isPixel(int pixel, bool reversed) {
    if (pixel >= width) { return false; }
    if (reversed) { pixel = width - pixel - 1; }
    if ((row_data[pixel/(8*sizeof(char))]>>(8*sizeof(char)-(pixel%(8*sizeof(char)))-1)) & 0x01) { return false; }
    else { return true; }
}

bool Bitmap::isPixel(int pixel) {
    return isPixel(pixel, false);
}

bool Bitmap::isBlankRow(void) {
    for (int i = 0; i < width; i++) {
        if (isPixel(i))
            return false;
    }
    return true;
}

Bitmap::Bitmap () {
    loaded = false;
    fp = NULL;
    row_data = NULL;
}

bool Bitmap::openImg(char* filename) {
    if (fp != NULL) {
        fclose(fp);
        free(row_data);
    }
    fp = fopen(filename, "rb");
    loaded = true;
    fseek(fp, OFFSET_LOCATION, SEEK_SET);
    fread((char *) &offset, 1, 4, fp);
    fseek(fp, WIDTH_LOCATION, SEEK_SET);
    fread((char *) &width, 1, 4, fp);
    fread(&height, sizeof(long), 1, fp);
    fseek(fp, HEIGHT_LOCATION, SEEK_SET);
    row_size = (width % 32) ? 4 * ((width / 32) + 1) :  4 * (width / 32);
    row_data = (char *) malloc(row_size * sizeof(char));
    return true;
}

bool Bitmap::setRow(int row) {
    if (loaded) {
        row_num = row;
        fseek(fp, offset + row * row_size*sizeof(char), SEEK_SET);
        fread(row_data, sizeof(char), row_size, fp);
        return true;
    } else {
        return false;
    }
}

bool Bitmap::closeImg(void) {
    fclose(fp);
    free(row_data);
    return true;
}

int Bitmap::getHeight() {
    return height;
}

int Bitmap::getWidth() {
    return width;
}
 