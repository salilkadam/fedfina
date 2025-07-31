# Android Integration Guide: WebView with ElevenLabs

## Overview

This guide provides step-by-step instructions for integrating the React application with ElevenLabs into an Android WebView, including parameter passing and webhook integration.

## Prerequisites

- Android Studio 4.0 or higher
- Android SDK API level 21 or higher
- Kotlin knowledge
- Basic understanding of WebView and JavaScript interfaces

## Project Setup

### 1. Add Dependencies

Add the following dependencies to your `app/build.gradle`:

```gradle
dependencies {
    implementation 'androidx.webkit:webkit:1.8.0'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'com.google.code.gson:gson:2.10.1'
    
    // For testing
    testImplementation 'junit:junit:4.13.2'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
}
```

### 2. Add Permissions

Add the following permissions to your `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.MODIFY_AUDIO_SETTINGS" />
```

## Implementation

### 1. Create WebView Activity

Create a new activity for the WebView:

```kotlin
class ConversationActivity : AppCompatActivity() {
    
    private lateinit var webView: WebView
    private lateinit var webViewClient: ConversationWebViewClient
    private lateinit var webChromeClient: ConversationWebChromeClient
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_conversation)
        
        setupWebView()
        loadConversationPage()
    }
    
    private fun setupWebView() {
        webView = findViewById(R.id.webView)
        
        // Configure WebView settings
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            mediaPlaybackRequiresUserGesture = false
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        }
        
        // Set up WebView clients
        webViewClient = ConversationWebViewClient()
        webChromeClient = ConversationWebChromeClient()
        
        webView.webViewClient = webViewClient
        webView.webChromeClient = webChromeClient
        
        // Add JavaScript interface
        webView.addJavascriptInterface(WebViewBridge(this), "Android")
    }
    
    private fun loadConversationPage() {
        val emailId = intent.getStringExtra("emailId") ?: ""
        val accountId = intent.getStringExtra("accountId") ?: ""
        val agentId = intent.getStringExtra("agentId") ?: "agent_01jxn7fwb2eyq8p6k4m3en4xtm"
        
        val url = buildString {
            append("https://your-domain.com/?")
            append("emailId=${URLEncoder.encode(emailId, "UTF-8")}")
            append("&accountId=${URLEncoder.encode(accountId, "UTF-8")}")
            if (agentId.isNotEmpty()) {
                append("&agentId=${URLEncoder.encode(agentId, "UTF-8")}")
            }
        }
        
        webView.loadUrl(url)
    }
}
```

### 2. Create WebView Layout

Create `activity_conversation.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</LinearLayout>
```

### 3. Create WebView Client

```kotlin
class ConversationWebViewClient : WebViewClient() {
    
    override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
        url?.let {
            // Handle external links if needed
            if (it.startsWith("tel:") || it.startsWith("mailto:")) {
                try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(it))
                    view?.context?.startActivity(intent)
                    return true
                } catch (e: Exception) {
                    Log.e("WebViewClient", "Error handling external link: $it", e)
                }
            }
        }
        return false
    }
    
    override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
        super.onPageStarted(view, url, favicon)
        // Show loading indicator
    }
    
    override fun onPageFinished(view: WebView?, url: String?) {
        super.onPageFinished(view, url)
        // Hide loading indicator
    }
    
    override fun onReceivedError(
        view: WebView?,
        request: WebResourceRequest?,
        error: WebResourceError?
    ) {
        super.onReceivedError(view, request, error)
        // Handle errors
        Log.e("WebViewClient", "WebView error: ${error?.description}")
    }
}
```

### 4. Create WebChrome Client

```kotlin
class ConversationWebChromeClient : WebChromeClient() {
    
    override fun onPermissionRequest(request: PermissionRequest?) {
        request?.let {
            // Handle permission requests for microphone access
            if (it.resources.contains(PermissionRequest.RESOURCE_AUDIO_CAPTURE)) {
                it.grant(it.resources)
            }
        }
    }
    
    override fun onConsoleMessage(message: ConsoleMessage?): Boolean {
        message?.let {
            Log.d("WebView", "${it.messageLevel()}: ${it.message()}")
        }
        return true
    }
}
```

### 5. Create JavaScript Bridge

```kotlin
class WebViewBridge(private val activity: Activity) {
    
    private val gson = Gson()
    
    @JavascriptInterface
    fun sendMessage(message: String) {
        // Handle messages from React app
        Log.d("WebViewBridge", "Received message: $message")
        
        activity.runOnUiThread {
            // Process message and take action if needed
            try {
                val messageData = gson.fromJson(message, MessageData::class.java)
                handleMessage(messageData)
            } catch (e: Exception) {
                Log.e("WebViewBridge", "Error parsing message", e)
            }
        }
    }
    
    @JavascriptInterface
    fun getParameters(): String {
        // Return parameters to React app
        val parameters = mapOf(
            "emailId" to (activity as? ConversationActivity)?.intent?.getStringExtra("emailId") ?: "",
            "accountId" to (activity as? ConversationActivity)?.intent?.getStringExtra("accountId") ?: "",
            "agentId" to (activity as? ConversationActivity)?.intent?.getStringExtra("agentId") ?: "",
            "platform" to "android",
            "version" to Build.VERSION.RELEASE,
            "deviceModel" to Build.MODEL
        )
        
        return gson.toJson(parameters)
    }
    
    @JavascriptInterface
    fun onConversationEnd(conversationData: String) {
        // Handle conversation end event
        Log.d("WebViewBridge", "Conversation ended: $conversationData")
        
        activity.runOnUiThread {
            try {
                val data = gson.fromJson(conversationData, ConversationEndData::class.java)
                handleConversationEnd(data)
            } catch (e: Exception) {
                Log.e("WebViewBridge", "Error parsing conversation data", e)
            }
        }
    }
    
    private fun handleMessage(messageData: MessageData) {
        // Handle different message types
        when (messageData.type) {
            "conversation_started" -> {
                // Handle conversation start
            }
            "conversation_ended" -> {
                // Handle conversation end
            }
            "error" -> {
                // Handle errors
                showError(messageData.content)
            }
        }
    }
    
    private fun handleConversationEnd(data: ConversationEndData) {
        // Send conversation data to your backend
        sendConversationToBackend(data)
        
        // Close activity or show summary
        activity.finish()
    }
    
    private fun sendConversationToBackend(data: ConversationEndData) {
        // Implement API call to your backend
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val apiService = ApiService()
                val response = apiService.sendConversation(data)
                
                withContext(Dispatchers.Main) {
                    if (response.isSuccessful) {
                        Log.d("WebViewBridge", "Conversation sent successfully")
                    } else {
                        Log.e("WebViewBridge", "Failed to send conversation")
                    }
                }
            } catch (e: Exception) {
                Log.e("WebViewBridge", "Error sending conversation", e)
            }
        }
    }
    
    private fun showError(message: String) {
        Toast.makeText(activity, message, Toast.LENGTH_LONG).show()
    }
}
```

### 6. Create Data Classes

```kotlin
data class MessageData(
    val type: String,
    val content: String,
    val timestamp: String? = null,
    val metadata: Map<String, Any>? = null
)

data class ConversationEndData(
    val emailId: String,
    val accountId: String,
    val conversationId: String,
    val transcript: List<TranscriptMessage>,
    val metadata: Map<String, Any>,
    val summary: ConversationSummary
)

data class TranscriptMessage(
    val timestamp: String,
    val speaker: String,
    val content: String,
    val messageId: String,
    val metadata: Map<String, Any>? = null
)

data class ConversationSummary(
    val topic: String,
    val sentiment: String,
    val resolution: String,
    val keywords: List<String>? = null,
    val intent: String? = null
)
```

### 7. Create API Service

```kotlin
class ApiService {
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private val gson = Gson()
    
    suspend fun sendConversation(data: ConversationEndData): Response {
        val json = gson.toJson(data)
        val requestBody = json.toRequestBody("application/json".toMediaType())
        
        val request = Request.Builder()
            .url("https://api.your-domain.com/api/v1/webhook/conversation")
            .addHeader("Authorization", "Bearer your-api-key")
            .addHeader("Content-Type", "application/json")
            .post(requestBody)
            .build()
        
        return withContext(Dispatchers.IO) {
            client.newCall(request).execute()
        }
    }
}
```

## Usage

### 1. Launch Conversation Activity

```kotlin
// From your main activity or fragment
val intent = Intent(this, ConversationActivity::class.java).apply {
    putExtra("emailId", "user@example.com")
    putExtra("accountId", "acc123")
    putExtra("agentId", "agent_01jxn7fwb2eyq8p6k4m3en4xtm") // Optional
}
startActivity(intent)
```

### 2. Handle Activity Result

```kotlin
override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    
    if (requestCode == CONVERSATION_REQUEST_CODE) {
        when (resultCode) {
            Activity.RESULT_OK -> {
                // Conversation completed successfully
                val conversationId = data?.getStringExtra("conversationId")
                // Handle success
            }
            Activity.RESULT_CANCELED -> {
                // Conversation was cancelled
                // Handle cancellation
            }
        }
    }
}
```

## Configuration

### 1. Environment Configuration

Create a configuration file for different environments:

```kotlin
object Config {
    const val PRODUCTION_URL = "https://your-domain.com"
    const val STAGING_URL = "https://staging.your-domain.com"
    const val DEVELOPMENT_URL = "https://dev.your-domain.com"
    
    const val API_BASE_URL = "https://api.your-domain.com"
    const val API_KEY = "your-api-key"
    
    fun getBaseUrl(): String {
        return when (BuildConfig.BUILD_TYPE) {
            "release" -> PRODUCTION_URL
            "debug" -> DEVELOPMENT_URL
            else -> STAGING_URL
        }
    }
}
```

### 2. WebView Configuration

For better performance and security, add these additional settings:

```kotlin
webView.settings.apply {
    // Security settings
    allowFileAccessFromFileURLs = false
    allowUniversalAccessFromFileURLs = false
    
    // Performance settings
    cacheMode = WebSettings.LOAD_DEFAULT
    setRenderPriority(WebSettings.RenderPriority.HIGH)
    
    // Feature settings
    setGeolocationEnabled(false)
    setAppCacheEnabled(false)
    
    // User agent
    userAgentString = "$userAgentString AndroidApp/1.0"
}
```

## Testing

### 1. Unit Tests

```kotlin
class WebViewBridgeTest {
    
    @Test
    fun testGetParameters() {
        val activity = mock<ConversationActivity>()
        val intent = mock<Intent>()
        
        whenever(activity.intent).thenReturn(intent)
        whenever(intent.getStringExtra("emailId")).thenReturn("test@example.com")
        whenever(intent.getStringExtra("accountId")).thenReturn("test123")
        
        val bridge = WebViewBridge(activity)
        val parameters = bridge.getParameters()
        
        assertTrue(parameters.contains("test@example.com"))
        assertTrue(parameters.contains("test123"))
    }
}
```

### 2. Integration Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class ConversationActivityTest {
    
    @get:Rule
    val activityRule = ActivityScenarioRule(ConversationActivity::class.java)
    
    @Test
    fun testWebViewLoads() {
        onView(withId(R.id.webView))
            .check(matches(isDisplayed()))
    }
    
    @Test
    fun testJavaScriptEnabled() {
        activityRule.scenario.onActivity { activity ->
            val webView = activity.findViewById<WebView>(R.id.webView)
            assertTrue(webView.settings.javaScriptEnabled)
        }
    }
}
```

## Troubleshooting

### Common Issues

1. **JavaScript not working**
   - Ensure `javaScriptEnabled = true`
   - Check for JavaScript errors in logcat
   - Verify WebView client setup

2. **Audio not working**
   - Add microphone permissions
   - Handle permission requests in WebChromeClient
   - Test on physical device (emulator may have audio issues)

3. **Network errors**
   - Check internet permissions
   - Verify URL accessibility
   - Handle SSL certificate issues

4. **Performance issues**
   - Enable hardware acceleration
   - Optimize WebView settings
   - Monitor memory usage

### Debug Mode

Enable debug logging:

```kotlin
if (BuildConfig.DEBUG) {
    WebView.setWebContentsDebuggingEnabled(true)
}
```

### Error Handling

```kotlin
private fun handleWebViewError(error: WebResourceError?) {
    error?.let {
        when (it.errorCode) {
            ERROR_HOST_LOOKUP -> {
                // Network error
                showNetworkError()
            }
            ERROR_TIMEOUT -> {
                // Timeout error
                showTimeoutError()
            }
            else -> {
                // Other errors
                showGenericError()
            }
        }
    }
}
```

## Security Considerations

1. **Input Validation**: Validate all parameters passed to WebView
2. **HTTPS Only**: Use HTTPS URLs only in production
3. **JavaScript Interface**: Be careful with JavaScript interface methods
4. **File Access**: Disable file access when not needed
5. **Mixed Content**: Handle mixed content appropriately

## Performance Optimization

1. **Hardware Acceleration**: Enable hardware acceleration
2. **Caching**: Implement appropriate caching strategies
3. **Memory Management**: Monitor and manage WebView memory usage
4. **Network Optimization**: Use appropriate network settings

## Best Practices

1. **Error Handling**: Implement comprehensive error handling
2. **Loading States**: Show appropriate loading indicators
3. **User Feedback**: Provide clear user feedback for actions
4. **Accessibility**: Ensure WebView content is accessible
5. **Testing**: Test on multiple devices and Android versions 