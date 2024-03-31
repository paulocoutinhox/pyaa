import Swal from 'sweetalert2'
window.Swal = Swal

window.Toast = Swal.mixin({
  toast: true,
  position: 'bottom-start',
  iconColor: 'white',
  customClass: {
    popup: 'colored-toast',
  },
  showConfirmButton: false,
  timer: 5000,
  timerProgressBar: true,
  width: '32em'
})
