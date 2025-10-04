'use client'

import { Container } from '@/components/ui/Container'
import { Button } from '@/components/ui/Button'
import { Footer } from '@/components/sections/Footer'
import { Sparkles, Calendar, ArrowRight, TrendingUp, Zap, Users, Award, Rocket, BookOpen } from 'lucide-react'
import Link from 'next/link'

const featuredPost = {
  title: 'Planning Explorer Launches AI-Powered Approval Predictions',
  excerpt: 'Our new machine learning models can predict planning approval likelihood with 87% accuracy, helping property professionals make smarter investment decisions.',
  date: 'October 3, 2025',
  category: 'Product Updates',
  author: 'Planning Explorer Team',
  image: 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&h=600&fit=crop',
  readTime: '5 min read',
  link: '#article-1'
}

const newsArticles = [
  {
    title: 'New Feature: Timeline Forecasting for Planning Applications',
    excerpt: 'Predict when planning decisions will be made using our AI-powered timeline analysis.',
    date: 'September 28, 2025',
    category: 'Product Updates',
    readTime: '4 min read',
    icon: Zap,
    color: 'bg-cyan-50',
    link: '#article-2'
  },
  {
    title: 'Planning Explorer Secures £5M Series A Funding',
    excerpt: 'Led by PropTech Ventures, this funding will accelerate our AI development and UK market expansion.',
    date: 'September 15, 2025',
    category: 'Company News',
    readTime: '3 min read',
    icon: TrendingUp,
    color: 'bg-orange-50',
    link: '#article-3'
  },
  {
    title: 'Case Study: How Developers Save 90% Research Time',
    excerpt: 'Real-world success stories from property developers using Planning Explorer.',
    date: 'September 10, 2025',
    category: 'Case Studies',
    readTime: '6 min read',
    icon: Users,
    color: 'bg-pink-50',
    link: '#article-4'
  },
  {
    title: 'Winner: Best PropTech Innovation 2025',
    excerpt: 'Planning Explorer named Best PropTech Innovation at the UK Property Awards.',
    date: 'August 25, 2025',
    category: 'Awards',
    readTime: '2 min read',
    icon: Award,
    color: 'bg-green-50',
    link: '#article-5'
  },
  {
    title: 'Now Live: 336K+ UK Planning Applications Indexed',
    excerpt: 'Complete coverage of planning applications across England, Scotland, and Wales.',
    date: 'August 18, 2025',
    category: 'Product Updates',
    readTime: '3 min read',
    icon: Rocket,
    color: 'bg-yellow-50',
    link: '#article-6'
  },
  {
    title: 'Guide: Understanding AI Opportunity Scores',
    excerpt: 'Deep dive into how our AI calculates opportunity scores for planning applications.',
    date: 'August 5, 2025',
    category: 'Resources',
    readTime: '8 min read',
    icon: BookOpen,
    color: 'bg-cyan-50',
    link: '#article-7'
  }
]

const categories = [
  { name: 'All', count: 42, active: true },
  { name: 'Product Updates', count: 18 },
  { name: 'Company News', count: 12 },
  { name: 'Case Studies', count: 8 },
  { name: 'Resources', count: 4 }
]

const pressReleases = [
  {
    title: 'Planning Explorer Partners with Top 10 UK Property Developers',
    date: 'September 20, 2025',
    publication: 'Property Week',
    link: '#press-1'
  },
  {
    title: 'AI Revolution in UK Planning: Interview with Planning Explorer CEO',
    date: 'September 5, 2025',
    publication: 'The PropTech Times',
    link: '#press-2'
  },
  {
    title: 'Planning Intelligence Platform Raises £5M Series A',
    date: 'August 30, 2025',
    publication: 'TechCrunch',
    link: '#press-3'
  }
]

export default function NewsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Hero Section */}
      <section className="relative z-20 bg-gradient-to-br from-planning-primary via-planning-primary to-planning-accent overflow-hidden">
        <div className="absolute inset-0 overflow-hidden">
          <div className="w-full h-full bg-cover bg-center bg-no-repeat opacity-25" style={{backgroundImage: `url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop&crop=center')`}} />
          <div className="absolute inset-0 bg-gradient-to-br from-planning-primary/80 via-planning-primary/75 to-planning-accent/80"></div>
        </div>
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
          <div className="absolute top-20 left-10 w-64 h-64 bg-planning-bright/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-planning-button/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        <div className="relative z-10 py-20">
          <Container>
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 mb-6">
                <Sparkles className="w-4 h-4 text-planning-bright" />
                <span className="text-sm font-semibold text-white">News & Updates</span>
              </div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold mb-4 leading-tight" style={{ color: '#FFFFFF' }}>
                <span className="block">Latest News from</span>
                <span className="block">Planning Explorer</span>
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-white/90">
                Product updates, company news, case studies, and insights from the UK planning intelligence revolution.
              </p>
            </div>
          </Container>
        </div>
      </section>

      {/* Categories Filter */}
      <section className="py-12 bg-white relative -mt-10 z-30">
        <Container>
          <div className="flex flex-wrap justify-center gap-4">
            {categories.map((category, index) => (
              <button
                key={index}
                className={`px-6 py-3 rounded-full font-semibold text-sm transition-all ${
                  category.active
                    ? 'bg-planning-primary text-white'
                    : 'bg-gray-100 text-planning-text-light hover:bg-gray-200'
                }`}
              >
                {category.name} ({category.count})
              </button>
            ))}
          </div>
        </Container>
      </section>

      {/* Featured Article */}
      <section className="py-16 bg-white">
        <Container>
          <div className="max-w-6xl mx-auto">
            <div className="bg-gradient-to-br from-cyan-50 to-orange-50 rounded-3xl overflow-hidden hover:shadow-xl transition-all duration-300">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
                <div className="relative h-64 lg:h-auto">
                  <img
                    src={featuredPost.image}
                    alt={featuredPost.title}
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute top-4 left-4">
                    <span className="inline-block px-4 py-2 bg-planning-primary text-white text-xs font-bold rounded-full">
                      FEATURED
                    </span>
                  </div>
                </div>
                <div className="p-8 md:p-12 flex flex-col justify-center">
                  <div className="flex items-center gap-4 mb-4 text-sm text-planning-text-light">
                    <span className="px-3 py-1 bg-planning-primary/10 text-planning-primary rounded-full font-semibold">
                      {featuredPost.category}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {featuredPost.date}
                    </span>
                  </div>
                  <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4 leading-tight">
                    {featuredPost.title}
                  </h2>
                  <p className="text-planning-text-light mb-6 leading-relaxed text-lg">
                    {featuredPost.excerpt}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-planning-text-light">{featuredPost.readTime}</span>
                    <Link href={featuredPost.link}>
                      <Button className="bg-planning-primary text-white hover:bg-planning-accent">
                        Read Article
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </Container>
      </section>

      {/* Recent Articles */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-planning-primary mb-6">
              Recent Articles
            </h2>
            <p className="text-xl text-planning-text-light max-w-3xl mx-auto">
              Stay updated with the latest product releases, company news, and industry insights
            </p>
          </div>

          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {newsArticles.map((article, index) => (
              <div
                key={index}
                className={`${article.color} rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all duration-300`}
              >
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center mb-6 shadow-sm">
                  <article.icon className="w-8 h-8 text-planning-primary" />
                </div>
                <div className="flex items-center gap-3 mb-4 text-sm">
                  <span className="px-3 py-1 bg-planning-primary/10 text-planning-primary rounded-full font-semibold">
                    {article.category}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-planning-primary mb-3 leading-tight">
                  {article.title}
                </h3>
                <p className="text-planning-text-light mb-4 leading-relaxed text-sm">
                  {article.excerpt}
                </p>
                <div className="flex items-center justify-between text-sm text-planning-text-light mb-4">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {article.date}
                  </span>
                  <span>{article.readTime}</span>
                </div>
                <Link href={article.link}>
                  <Button size="sm" variant="outline" className="w-full">
                    Read More
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Button size="lg" variant="outline">
              Load More Articles
            </Button>
          </div>
        </Container>
      </section>

      {/* Press Releases */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-6">
                Press Releases & Media Coverage
              </h2>
              <p className="text-xl text-planning-text-light">
                Planning Explorer in the news
              </p>
            </div>

            <div className="space-y-6">
              {pressReleases.map((press, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded-3xl p-8 hover:shadow-lg transition-all duration-300 border-2 border-transparent hover:border-planning-primary/20"
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-planning-primary mb-2">{press.title}</h3>
                      <div className="flex flex-wrap items-center gap-4 text-sm text-planning-text-light">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          {press.date}
                        </span>
                        <span className="font-semibold text-planning-primary">{press.publication}</span>
                      </div>
                    </div>
                    <Link href={press.link}>
                      <Button variant="outline">
                        Read Article
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-center mt-12 p-8 bg-gradient-to-br from-planning-primary to-planning-accent rounded-3xl text-white">
              <h3 className="text-2xl font-bold mb-4">Media Inquiries</h3>
              <p className="text-white/90 mb-6">
                For press releases, media kits, and interview requests
              </p>
              <Link href="/contact?subject=Media Inquiry">
                <Button size="lg" className="bg-white text-planning-primary hover:bg-gray-100">
                  Contact Press Team
                </Button>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      {/* Newsletter Signup */}
      <section className="py-24 bg-gray-50">
        <Container>
          <div className="max-w-3xl mx-auto text-center">
            <div className="bg-white rounded-3xl shadow-lg p-8 md:p-12">
              <Sparkles className="w-16 h-16 text-planning-primary mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-4">
                Stay Updated
              </h2>
              <p className="text-xl text-planning-text-light mb-8">
                Get the latest product updates, case studies, and planning industry insights delivered to your inbox
              </p>
              <form className="flex flex-col sm:flex-row gap-4 max-w-2xl mx-auto">
                <input
                  type="email"
                  placeholder="Enter your email address"
                  className="flex-1 px-6 py-4 border-2 border-planning-border rounded-2xl focus:border-planning-primary focus:outline-none transition-colors"
                  required
                />
                <Button type="submit" size="lg" className="bg-planning-primary text-white hover:bg-planning-accent whitespace-nowrap">
                  Subscribe
                </Button>
              </form>
              <p className="text-sm text-planning-text-light mt-4">
                We respect your privacy. Unsubscribe anytime. See our{' '}
                <Link href="/privacy" className="text-planning-primary hover:underline">
                  Privacy Policy
                </Link>
              </p>
            </div>
          </div>
        </Container>
      </section>

      {/* Quick Links */}
      <section className="py-24 bg-white">
        <Container>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-planning-primary mb-8">
              Explore More Resources
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link href="/tutorials">
                <div className="bg-cyan-50 rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all cursor-pointer">
                  <BookOpen className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">Tutorials</h3>
                  <p className="text-sm text-planning-text-light">Learn how to use Planning Explorer</p>
                </div>
              </Link>
              <Link href="/about">
                <div className="bg-orange-50 rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all cursor-pointer">
                  <Users className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">About Us</h3>
                  <p className="text-sm text-planning-text-light">Our mission and team</p>
                </div>
              </Link>
              <Link href="/careers">
                <div className="bg-pink-50 rounded-3xl p-8 hover:shadow-lg hover:scale-105 transition-all cursor-pointer">
                  <Rocket className="w-12 h-12 text-planning-primary mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-planning-primary mb-2">Careers</h3>
                  <p className="text-sm text-planning-text-light">Join our team</p>
                </div>
              </Link>
            </div>
          </div>
        </Container>
      </section>

      <Footer />
    </div>
  )
}
