from typing import Any, Dict, Optional, Union

import PIL.Image

import torch
from torchvision.prototype import features
from torchvision.prototype.transforms import functional as F, Transform


class ConvertBoundingBoxFormat(Transform):
    _transformed_types = (features.BoundingBox,)

    def __init__(self, format: Union[str, features.BoundingBoxFormat]) -> None:
        super().__init__()
        if isinstance(format, str):
            format = features.BoundingBoxFormat[format]
        self.format = format

    def _transform(self, inpt: features.BoundingBox, params: Dict[str, Any]) -> features.BoundingBox:
        # We need to unwrap here to avoid unnecessary `__torch_function__` calls,
        # since `convert_format_bounding_box` does not have a dispatcher function that would do that for us
        output = F.convert_format_bounding_box(
            inpt.as_subclass(torch.Tensor), old_format=inpt.format, new_format=params["format"]
        )
        return features.BoundingBox.wrap_like(inpt, output, format=params["format"])


class ConvertImageDtype(Transform):
    _transformed_types = (features.is_simple_tensor, features.Image, features.Video)

    def __init__(self, dtype: torch.dtype = torch.float32) -> None:
        super().__init__()
        self.dtype = dtype

    def _transform(
        self, inpt: Union[features.TensorImageType, features.TensorVideoType], params: Dict[str, Any]
    ) -> Union[features.TensorImageType, features.TensorVideoType]:
        # TODO: the `inpt.as_subclass(torch.Tensor)` call can be removed as soon as we have a proper dispatcher that
        #  handles this. See https://github.com/pytorch/vision/pull/6783 for details.
        output = F.convert_image_dtype(inpt.as_subclass(torch.Tensor), dtype=self.dtype)
        return (
            output if features.is_simple_tensor(inpt) else type(inpt).wrap_like(inpt, output)  # type: ignore[attr-defined]
        )


class ConvertColorSpace(Transform):
    _transformed_types = (features.is_simple_tensor, features.Image, PIL.Image.Image, features.Video)

    def __init__(
        self,
        color_space: Union[str, features.ColorSpace],
        old_color_space: Optional[Union[str, features.ColorSpace]] = None,
    ) -> None:
        super().__init__()

        if isinstance(color_space, str):
            color_space = features.ColorSpace.from_str(color_space)
        self.color_space = color_space

        if isinstance(old_color_space, str):
            old_color_space = features.ColorSpace.from_str(old_color_space)
        self.old_color_space = old_color_space

    def _transform(
        self, inpt: Union[features.ImageType, features.VideoType], params: Dict[str, Any]
    ) -> Union[features.ImageType, features.VideoType]:
        return F.convert_color_space(inpt, color_space=self.color_space, old_color_space=self.old_color_space)


class ClampBoundingBoxes(Transform):
    _transformed_types = (features.BoundingBox,)

    def _transform(self, inpt: features.BoundingBox, params: Dict[str, Any]) -> features.BoundingBox:
        # We need to unwrap here to avoid unnecessary `__torch_function__` calls,
        # since `clamp_bounding_box` does not have a dispatcher function that would do that for us
        output = F.clamp_bounding_box(
            inpt.as_subclass(torch.Tensor), format=inpt.format, spatial_size=inpt.spatial_size
        )
        return features.BoundingBox.wrap_like(inpt, output)
