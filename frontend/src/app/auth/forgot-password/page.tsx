import { PasswordReset } from '@/components/user/Auth/PasswordReset'

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-planning-primary rounded-lg flex items-center justify-center mb-6">
            <span className="text-white font-bold text-xl">PE</span>
          </div>
          <h2 className="text-3xl font-bold text-planning-primary">
            Planning Explorer
          </h2>
          <p className="mt-2 text-planning-text-light">
            AI-Powered Planning Intelligence Platform
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <PasswordReset />
      </div>
    </div>
  )
}