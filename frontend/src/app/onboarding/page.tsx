import { Onboarding } from '@/components/user/Auth/Onboarding'

export default function OnboardingPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-planning-primary rounded-lg flex items-center justify-center mb-6">
            <span className="text-white font-bold text-xl">PE</span>
          </div>
          <h2 className="text-3xl font-bold text-planning-primary">
            Welcome to Planning Explorer
          </h2>
          <p className="mt-2 text-planning-text-light">
            Let's set up your account to get personalized insights
          </p>
        </div>

        <Onboarding />
      </div>
    </div>
  )
}