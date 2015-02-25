/*
############################################################################
#    Copyright (C) 2008 by Lukas Sandström                                 #
#    luksan@gmail.com                                                      #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################
*/

%module pyfprint_swig
%{
#include <libfprint/fprint.h>
#include <errno.h>
%}

%feature("autodoc", "1");

%include <typemaps.i>
%include <cdata.i>
%include <carrays.i>
%include <cstring.i>

%nodefaultctor;

/* fp_dev_img_capture,  fp_enroll_finger_img, fp_verify_finger_img, fp_identify_finger_img */
%typemap(argout) struct fp_img ** {
    PyObject *o;
    o = SWIG_NewPointerObj(*$1, $*1_descriptor, 1);
    $result = SWIG_AppendOutput($result, o);
    /* FIXME: is a PY_DECREF(o) needed here ?*/
}
%typemap(in, numinputs=0) struct fp_img **(struct fp_img *img) {
    $1 = &img;
}

/* fp_enroll_finger_img */
%typemap(argout) struct fp_print_data **print_data = struct fp_img **;
%typemap(in, numinputs=0) struct fp_print_data **print_data(struct fp_print_data *data) {
    $1 = &data;
}

/* fp_print_data_load, fp_print_data_from_dscv_print */
%apply struct fp_print_data **print_data { struct fp_print_data **data };

/* fp_identify_finger */
%apply unsigned long *OUTPUT { size_t *match_offset };

/* fp_print_data_from_data */
%apply (char *STRING, int LENGTH) { (unsigned char *buf, size_t buflen) };

/* fp_img_get_minutiae */
%apply int *OUTPUT { int *nr_minutiae };

/* Tell SWIG that we're freeing the pointers */
%delobject fp_dscv_devs_free;
%delobject fp_img_free;
%delobject fp_print_data_free;
%delobject fp_dscv_prints_free;
%delobject fp_dev_close;
%delobject pyfp_free_print_data_array;

/* Tell SWIG that we're allocating new objects */
%newobject pyfp_alloc_print_data_array;
%newobject fp_dev_open;

/* Image.get_minutiae() */
%inline %{
struct fp_minutia * pyfp_deref_minutiae(struct fp_minutia **ptr, int i)
{
	return ptr[i];
}

%}
/* The struct needs to be redefined as const, otherwise swig will generate _set_ methods for the members. */
struct fp_minutia {
	const int x;
	const int y;
	const int ex;
	const int ey;
	const int direction;
	const double reliability;
	const int type;
	const int appearing;
	const int feature_id;
	int * const nbrs;
	int * const ridge_counts;
	const int num_nbrs;

	%extend {
		/* A constructor that accepts pre-allocated structs */
		fp_minutia(struct fp_minutia *ptr)
		{
			return ptr;
		}
		~fp_minutia()
		{
			/* Don't free() fp_minutia *. They are free'd together with the fp_img. */ ;
		}
	};
};

/* Needed to get correct output from
   fp_dscv_print_get_driver_id and fp_dev_get_devtype */
typedef unsigned int uint32_t;
/* fp_driver_get_driver_id, fp_dscv_print_get_driver_id, fp_print_data_get_driver_id*/
typedef unsigned short int uint16_t;

/* Fprint.get_data() */
%cstring_output_allocate_size(char **print_data, int *len, free(*($1)));
%inline %{
void pyfp_print_get_data(char **print_data, int *len, struct fp_print_data *print)
{
	*len = fp_print_data_get_data(print, (unsigned char**)print_data);
}
%}

/* Img.get_data() */
%cstring_output_allocate_size(char **img_data, int *len, "");
%inline %{
void pyfp_img_get_data(char **img_data, int *len, struct fp_img *img)
{
	*img_data = fp_img_get_data(img);
	*len = fp_img_get_width(img) * fp_img_get_height(img);
}
%}

/* Image.get_rgb_data() */
%cstring_output_allocate_size(char **img_rgb_data, int *len, free(*($1)));
%inline %{
void pyfp_img_get_rgb_data(char **img_rgb_data, int *len, struct fp_img *img)
{
	unsigned int i, j = 0;
	unsigned char *img_data = fp_img_get_data(img);
	*len = fp_img_get_width(img) * fp_img_get_height(img) * 3;
	(*img_rgb_data) = malloc(*len);
	for (i = 0; i < (*len)/3; i++) {
		(*img_rgb_data)[j++] = img_data[i];
		(*img_rgb_data)[j++] = img_data[i];
		(*img_rgb_data)[j++] = img_data[i];
	}
}
%}

/* Wrappers to let Python yield the thread */
%inline %{
int pyfp_enroll_finger_img(struct fp_dev *dev, struct fp_print_data **print_data, struct fp_img **img)
{
	int ret;
	Py_BEGIN_ALLOW_THREADS
	ret = fp_enroll_finger_img(dev, print_data, img);
	Py_END_ALLOW_THREADS
	return ret;
}
int pyfp_verify_finger_img(struct fp_dev *dev, struct fp_print_data *enrolled_print, struct fp_img **img)
{
	int ret;
	Py_BEGIN_ALLOW_THREADS
	ret = fp_verify_finger_img(dev, enrolled_print, img);
	Py_END_ALLOW_THREADS
	return ret;
}
int pyfp_identify_finger_img(struct fp_dev *dev, struct fp_print_data **print_gallery, size_t *match_offset, struct fp_img **img)
{
	int ret;
	Py_BEGIN_ALLOW_THREADS
	ret = fp_identify_finger_img(dev, print_gallery, match_offset, img);
	Py_END_ALLOW_THREADS
	return ret;
}
int pyfp_dev_img_capture(struct fp_dev *dev, int unconditional, struct fp_img **image)
{
	int ret;
	Py_BEGIN_ALLOW_THREADS
	ret = fp_dev_img_capture(dev, unconditional, image);
	Py_END_ALLOW_THREADS
	return ret;
}
%}

/* Device.identify_finger() */
%inline %{
struct pyfp_print_data_array {
	size_t size;
	size_t used;
	struct fp_print_data * list[0];
};
%}
%extend pyfp_print_data_array {
	pyfp_print_data_array(size_t size)
	{
		struct pyfp_print_data_array *x;
		x = calloc(1, sizeof(struct pyfp_print_data_array) +
				sizeof(struct fp_print_data *) * (size + 1)); /* +1 for NULL termination */
		x->size = size;
		return x;
	}
	~pyfp_print_data_array()
	{
		free($self);
	}
	void append(struct fp_print_data *print)
	{
		if ($self->size <= $self->used) {
			PyErr_SetString(PyExc_OverflowError, "programming error: pyfp_print_data_array list overflow");
			return;
		}
		$self->list[$self->used] = print;
		$self->used++;
	}
	struct fp_print_data ** pyfp_print_data_array_list_get()
	{
		return $self->list;
	}
};

%inline %{

/* DiscoveredDevices.__init__() */
struct fp_dscv_dev * pyfp_deref_dscv_dev_ptr (struct fp_dscv_dev **ptr, int i)
{
	return ptr[i];
}

/* class DiscoveredPrints(list): */
struct fp_dscv_print * pyfp_deref_dscv_print_ptr(struct fp_dscv_print **ptr, int i)
{
	return ptr[i];
}

%}

/* --- partial copy of <libfprint/fprint.h> --- */

/*
 * Main definitions for libfprint
 * Copyright (C) 2007 Daniel Drake <dsd@gentoo.org>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 */

/* structs that applications are not allowed to peek into */
struct fp_dscv_dev;
struct fp_dscv_print;
struct fp_dev;
struct fp_driver;
struct fp_print_data;
struct fp_img;

/* misc/general stuff */

/** \ingroup print_data
 * Numeric codes used to refer to fingers (and thumbs) of a human. These are
 * purposely not available as strings, to avoid getting the library tangled up
 * in localization efforts.
 */
enum fp_finger {
	LEFT_THUMB = 1, /** thumb (left hand) */
	LEFT_INDEX, /** index finger (left hand) */
	LEFT_MIDDLE, /** middle finger (left hand) */
	LEFT_RING, /** ring finger (left hand) */
	LEFT_LITTLE, /** little finger (left hand) */
	RIGHT_THUMB, /** thumb (right hand) */
	RIGHT_INDEX, /** index finger (right hand) */
	RIGHT_MIDDLE, /** middle finger (right hand) */
	RIGHT_RING, /** ring finger (right hand) */
	RIGHT_LITTLE, /** little finger (right hand) */
};

/* Drivers */
const char *fp_driver_get_name(struct fp_driver *drv);
const char *fp_driver_get_full_name(struct fp_driver *drv);
uint16_t fp_driver_get_driver_id(struct fp_driver *drv);

/* Device discovery */
struct fp_dscv_dev **fp_discover_devs(void);
void fp_dscv_devs_free(struct fp_dscv_dev **devs);
struct fp_driver *fp_dscv_dev_get_driver(struct fp_dscv_dev *dev);
uint32_t fp_dscv_dev_get_devtype(struct fp_dscv_dev *dev);
int fp_dscv_dev_supports_print_data(struct fp_dscv_dev *dev,
	struct fp_print_data *print);
int fp_dscv_dev_supports_dscv_print(struct fp_dscv_dev *dev,
	struct fp_dscv_print *print);
struct fp_dscv_dev *fp_dscv_dev_for_print_data(struct fp_dscv_dev **devs,
	struct fp_print_data *print);
struct fp_dscv_dev *fp_dscv_dev_for_dscv_print(struct fp_dscv_dev **devs,
	struct fp_dscv_print *print);

static inline uint16_t fp_dscv_dev_get_driver_id(struct fp_dscv_dev *dev)
{
	return fp_driver_get_driver_id(fp_dscv_dev_get_driver(dev));
}

/* Print discovery */
struct fp_dscv_print **fp_discover_prints(void);
void fp_dscv_prints_free(struct fp_dscv_print **prints);
uint16_t fp_dscv_print_get_driver_id(struct fp_dscv_print *print);
uint32_t fp_dscv_print_get_devtype(struct fp_dscv_print *print);
enum fp_finger fp_dscv_print_get_finger(struct fp_dscv_print *print);
int fp_dscv_print_delete(struct fp_dscv_print *print);

/* Device handling */
struct fp_dev *fp_dev_open(struct fp_dscv_dev *ddev);
void fp_dev_close(struct fp_dev *dev);
struct fp_driver *fp_dev_get_driver(struct fp_dev *dev);
int fp_dev_get_nr_enroll_stages(struct fp_dev *dev);
uint32_t fp_dev_get_devtype(struct fp_dev *dev);
int fp_dev_supports_print_data(struct fp_dev *dev, struct fp_print_data *data);
int fp_dev_supports_dscv_print(struct fp_dev *dev, struct fp_dscv_print *print);

int fp_dev_supports_imaging(struct fp_dev *dev);
int fp_dev_get_img_width(struct fp_dev *dev);
int fp_dev_get_img_height(struct fp_dev *dev);

/** \ingroup dev
 * Enrollment result codes returned from fp_enroll_finger().
 * Result codes with RETRY in the name suggest that the scan failed due to
 * user error. Applications will generally want to inform the user of the
 * problem and then retry the enrollment stage. For more info on the semantics
 * of interpreting these result codes and tracking enrollment process, see
 * \ref enrolling.
 */
enum fp_enroll_result {
	/** Enrollment completed successfully, the enrollment data has been
	 * returned to the caller. */
	FP_ENROLL_COMPLETE = 1,
	/** Enrollment failed due to incomprehensible data; this may occur when
	 * the user scans a different finger on each enroll stage. */
	FP_ENROLL_FAIL,
	/** Enroll stage passed; more stages are need to complete the process. */
	FP_ENROLL_PASS,
	/** The enrollment scan did not succeed due to poor scan quality or
	 * other general user scanning problem. */
	FP_ENROLL_RETRY = 100,
	/** The enrollment scan did not succeed because the finger swipe was
	 * too short. */
	FP_ENROLL_RETRY_TOO_SHORT,
	/** The enrollment scan did not succeed because the finger was not
	 * centered on the scanner. */
	FP_ENROLL_RETRY_CENTER_FINGER,
	/** The verification scan did not succeed due to quality or pressure
	 * problems; the user should remove their finger from the scanner before
	 * retrying. */
	FP_ENROLL_RETRY_REMOVE_FINGER,
};

/** \ingroup dev
 * Verification result codes returned from fp_verify_finger(). Return codes
 * are also shared with fp_identify_finger().
 * Result codes with RETRY in the name suggest that the scan failed due to
 * user error. Applications will generally want to inform the user of the
 * problem and then retry the verify operation.
 */
enum fp_verify_result {
	/** The scan completed successfully, but the newly scanned fingerprint
	 * does not match the fingerprint being verified against.
	 * In the case of identification, this return code indicates that the
	 * scanned finger could not be found in the print gallery. */
	FP_VERIFY_NO_MATCH = 0,
	/** The scan completed successfully and the newly scanned fingerprint does
	 * match the fingerprint being verified, or in the case of identification,
	 * the scanned fingerprint was found in the print gallery. */
	FP_VERIFY_MATCH = 1,
	/** The scan did not succeed due to poor scan quality or other general
	 * user scanning problem. */
	FP_VERIFY_RETRY = FP_ENROLL_RETRY,
	/** The scan did not succeed because the finger swipe was too short. */
	FP_VERIFY_RETRY_TOO_SHORT = FP_ENROLL_RETRY_TOO_SHORT,
	/** The scan did not succeed because the finger was not centered on the
	 * scanner. */
	FP_VERIFY_RETRY_CENTER_FINGER = FP_ENROLL_RETRY_CENTER_FINGER,
	/** The scan did not succeed due to quality or pressure problems; the user
	 * should remove their finger from the scanner before retrying. */
	FP_VERIFY_RETRY_REMOVE_FINGER = FP_ENROLL_RETRY_REMOVE_FINGER,
};

int fp_dev_supports_identification(struct fp_dev *dev);

/* Data handling */
int fp_print_data_load(struct fp_dev *dev, enum fp_finger finger,
	struct fp_print_data **data);
int fp_print_data_from_dscv_print(struct fp_dscv_print *print,
	struct fp_print_data **data);
int fp_print_data_save(struct fp_print_data *data, enum fp_finger finger);
int fp_print_data_delete(struct fp_dev *dev, enum fp_finger finger);
void fp_print_data_free(struct fp_print_data *data);
struct fp_print_data *fp_print_data_from_data(unsigned char *buf,
	size_t buflen);
uint16_t fp_print_data_get_driver_id(struct fp_print_data *data);
uint32_t fp_print_data_get_devtype(struct fp_print_data *data);

/* Image handling */

int fp_img_get_height(struct fp_img *img);
int fp_img_get_width(struct fp_img *img);
int fp_img_save_to_file(struct fp_img *img, char *path);
void fp_img_standardize(struct fp_img *img);
struct fp_img *fp_img_binarize(struct fp_img *img);
struct fp_minutia **fp_img_get_minutiae(struct fp_img *img, int *nr_minutiae);
void fp_img_free(struct fp_img *img);

/* Library */
int fp_init(void);
void fp_exit(void);

/* -------- END OF COPY ---------- */
