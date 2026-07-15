import { BrowserRouter } from 'react-router-dom'
import AuthProvider from './context/AuthContext'
import AppRoutes from './routes'
import ToastContainer from './components/ToastContainer'

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <ToastContainer />
      </AuthProvider>
    </BrowserRouter>
  )
}