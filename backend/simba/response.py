from rest_framework import status, viewsets

from core.utils import APIResponse


class BaseResponseViewSet(viewsets.ModelViewSet, APIResponse):
	"""
	A base ViewSet that wraps all responses in a standard format.
	"""

	# def list - filter by user

	def create(self, request, *args, **kwargs):
		try:
			response = super().create(request, *args, **kwargs)
			return self.success(
				success=True,
				message="Created successfully",
				data=response.data,
				status=status.HTTP_201_CREATED,
			)
		except Exception:
			self.error(
				success=False,
				# todo: erro handling conversion to generate message
				message="An error occured",
				data=None,
				status=self.status_code,
			)

	def update(self, request, *args, **kwargs):
		try:
			kwargs["partial"] = True
			response = super().update(request, *args, **kwargs)
			return self.success(
				success=True,
				message="Updated successfully",
				data=response.data,
				status=status.HTTP_200_OK,
			)
		except Exception:
			self.error(
				success=False,
				# todo: erro handling conversion to generate message
				message="An error occured",
				data=None,
				status=self.status_code,
			)

	def destroy(self, request, *args, **kwargs):
		try:
			super().destroy(request, *args, **kwargs)
			return self.success(
				success=True,
				message="Deleted successfully",
				data=None,
				status=status.HTTP_204_NO_CONTENT,
			)
		except Exception:
			self.error(
				success=False,
				# todo: erro handling conversion to generate message
				message="An error occured",
				data=None,
				status=self.status_code,
			)
